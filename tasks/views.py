from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer, TaskStatusUpdateSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    """
    Create a new task for the authenticated user
    """
    serializer = TaskSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        task = serializer.save()
        return Response({
            'message': 'Task created successfully',
            'task': TaskSerializer(task).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tasks(request):
    """
    List all tasks for the authenticated user
    """
    tasks = Task.objects.filter(user=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail(request, task_id):
    """
    Retrieve, update or delete a task
    """
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data, context={'request': request})
        if serializer.is_valid():
            updated_task = serializer.save()
            return Response({
                'message': 'Task updated successfully',
                'task': TaskSerializer(updated_task).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        task.delete()
        return Response({'message': 'Task deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_status(request, task_id):
    """
    Update the status of a specific task
    """
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TaskStatusUpdateSerializer(task, data=request.data, partial=True)
    
    if serializer.is_valid():
        updated_task = serializer.save()
        return Response({
            'message': 'Task status updated successfully',
            'task': TaskSerializer(updated_task).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
