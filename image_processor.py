from PIL import Image
import io

def optimize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """Оптимизирует изображение, уменьшая его размер и качество."""
    # Изменяем размер изображения, сохраняя пропорции
    image.thumbnail((max_size, max_size))
    
    # Конвертируем в RGB, если изображение в режиме RGBA
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Сжимаем изображение
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85, optimize=True)
    
    return Image.open(buffered)