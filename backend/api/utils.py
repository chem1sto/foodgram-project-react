from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def post(request, pk, model, serializer):
    """Обработка POST-запроса для списков "Избранное" или списков покупок."""
    recipe = get_object_or_404(Recipe, pk=pk)
    if model.objects.filter(user=request.user, recipe=recipe).exists():
        return Response(
            {'errors': 'Рецепт уже в списке "Избранное" или списке покупок'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    model.objects.get_or_create(user=request.user, recipe=recipe)
    serializer = serializer(
        instance=recipe,
        context={'request': request}
    )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete(request, pk, model):
    """Обработка DELETE-запроса для списков "Избранное" или списков покупок."""
    recipe = get_object_or_404(Recipe, pk=pk)
    if model.objects.filter(user=request.user, recipe=recipe).exists():
        obj = get_object_or_404(
            klass=model,
            user=request.user,
            recipe=recipe
        )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': 'Рецепта нет в списке "Избранное" или списке покупок'},
        status=status.HTTP_400_BAD_REQUEST
    )
