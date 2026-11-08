import csv
import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import PaymentLog
from .services import (
    PaymentError,
    apply_webhook,
    complete_sandbox,
    create_order,
    filtered_transactions,
    get_client_ip,
    mark_failed,
    order_payload,
    owned_transaction,
    paginate_transactions,
    payment_mode,
    refund_transaction,
    safe_compare,
    serialize_activity,
    serialize_transaction,
    sign_webhook,
    summary_for,
    verify_payment,
)


def guarded(action):
    try:
        return action()
    except PaymentError as exc:
        return Response({'error': exc.message}, status=exc.status)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_api(request):
    try:
        mode = payment_mode()
    except PaymentError:
        mode = 'misconfigured'
    return Response({'status': 'ok', 'payment_mode': mode})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_api(request):
    def action():
        transaction = create_order(
            request.user,
            request.data.get('amount'),
            request.data.get('description'),
            get_client_ip(request),
        )
        return Response(order_payload(transaction, request.user))

    return guarded(action)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment_api(request):
    def action():
        transaction = verify_payment(
            request.user,
            request.data.get('razorpay_order_id'),
            request.data.get('razorpay_payment_id'),
            request.data.get('razorpay_signature'),
            get_client_ip(request),
        )
        return Response({
            'message': 'Payment successful.',
            'transaction': serialize_transaction(transaction),
        })

    return guarded(action)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payment_failure_api(request):
    def action():
        transaction = mark_failed(
            request.user,
            request.data.get('transaction_id'),
            request.data.get('reason') or 'Payment failed or was cancelled.',
            get_client_ip(request),
        )
        return Response({
            'message': 'Payment marked as failed.',
            'transaction': serialize_transaction(transaction),
        })

    return guarded(action)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sandbox_complete_api(request):
    def action():
        transaction = complete_sandbox(
            request.user,
            request.data.get('transaction_id'),
            request.data.get('outcome'),
            get_client_ip(request),
        )
        return Response({
            'message': 'Sandbox payment recorded.',
            'transaction': serialize_transaction(transaction),
        })

    return guarded(action)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history_api(request):
    return Response(paginate_transactions(
        request.user,
        status=request.query_params.get('status', ''),
        query=request.query_params.get('q', ''),
        page=request.query_params.get('page', 1),
    ))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_summary_api(request):
    return Response(summary_for(request.user))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_detail_api(request, transaction_id):
    def action():
        transaction = owned_transaction(request.user, id=transaction_id)
        logs = PaymentLog.objects.filter(transaction=transaction).order_by('created_at', 'id')
        payload = serialize_transaction(transaction)
        payload['activity'] = [serialize_activity(log) for log in logs]
        return Response(payload)

    return guarded(action)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refund_api(request, transaction_id):
    def action():
        transaction = refund_transaction(request.user, transaction_id, get_client_ip(request))
        return Response({
            'message': 'Payment refunded.',
            'transaction': serialize_transaction(transaction),
        })

    return guarded(action)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_transactions_api(request):
    rows = filtered_transactions(
        request.user,
        status=request.query_params.get('status', ''),
        query=request.query_params.get('q', ''),
    )[:1000]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="paygate-transactions.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Description', 'Amount', 'Currency', 'Status', 'Provider', 'Payment ID', 'Created'])
    for item in rows:
        writer.writerow([
            item.order_id,
            item.description,
            f'{item.amount:.2f}',
            item.currency,
            item.status,
            item.provider,
            item.razorpay_payment_id,
            item.created_at.isoformat(),
        ])
    return response


@csrf_exempt
def webhook_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

    signature = request.headers.get('X-Razorpay-Signature', '')
    if not safe_compare(sign_webhook(request.body), signature):
        return JsonResponse({'error': 'Invalid webhook signature.'}, status=400)

    try:
        payload = json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    return JsonResponse({'status': apply_webhook(payload)})
