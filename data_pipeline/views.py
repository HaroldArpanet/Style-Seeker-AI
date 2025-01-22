from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from tempfile import NamedTemporaryFile
import os
from data_pipeline.tasks import index_data_flow
import threading

class TriggerIndexFlowView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get('data_file')
        index_name = request.data.get('index_name')
        if not uploaded_file:
            return Response(
                {
                    "error": "Json file is require."
                },
                status=status.HTTP_400_BAD_REQUEST,
            ) 
        elif not index_name:
            return Response(
                {
                    "error": "Index Name is require."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            flow_thread = threading.Thread(target=index_data_flow, args=(tmp_file_path, index_name))
            flow_thread.start()

            return Response(
                {
                    "status": "Flow for data import has been triggered and is running in the background."
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "error": f"An error occurred: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
