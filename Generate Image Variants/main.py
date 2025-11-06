import os
from torchvision import transforms
from PIL import Image


class RandomRotateNoBlackEdge:
    def __init__(self, degrees=5, bleed=5):
        """
        degrees: 最大旋轉角度（±degrees）
        bleed:   出血線（往內多裁掉的像素數）
        """
        if isinstance(degrees, (int, float)):
            self.degrees = (-degrees, degrees)
        else:
            self.degrees = degrees
        self.bleed = int(bleed)

    def __call__(self, img: Image.Image) -> Image.Image:
        # 角度
        angle = transforms.RandomRotation.get_params(self.degrees)

        # 旋轉 (RGBA)
        img_rgba = img.convert("RGBA")
        rotated = img_rgba.rotate(
            angle,
            resample=Image.BICUBIC,
            expand=True
        )

        # 3. 先依 alpha 抓「非透明」外框
        alpha = rotated.split()[3]
        bbox = alpha.getbbox()
        if bbox:
            left, top, right, bottom = bbox

            # 出血線
            bleed = self.bleed
            left   += bleed
            top    += bleed
            right  -= bleed
            bottom -= bleed

            # 防止超出界
            left   = max(0, left)
            top    = max(0, top)
            right  = min(rotated.width, right)
            bottom = min(rotated.height, bottom)

            # 只有在仍有面積時才裁切
            if right > left and bottom > top:
                bbox = (left, top, right, bottom)
                rotated = rotated.crop(bbox)
                alpha   = alpha.crop(bbox)

        # 5. 貼到白色背景（避免黑邊）
        bg = Image.new('RGB', rotated.size, (255, 255, 255))
        bg.paste(rotated, mask=alpha)

        return bg


def generate_variants(
    input_path: str,
    output_dir: str = 'output',
    num_variants: int = 10,
    degrees: int | float = 3,
    bleed: int = 30,
):
    """
    input_path : 原始圖片路徑，例如 'input.jpg'
    output_dir : 輸出資料夾名稱
    num_variants : 要產生幾張增強後圖片
    degrees : 最大旋轉角度（±degrees）
    bleed : 出血線（往內多裁掉的像素數）
    """
    os.makedirs(output_dir, exist_ok=True)

    img = Image.open(input_path).convert('RGB')

    transform = transforms.Compose([
        RandomRotateNoBlackEdge(degrees=degrees, bleed=bleed),
        transforms.ColorJitter(
            brightness=0.02,        # 亮度
            contrast=0.02,          # 對比
            saturation=0.01,        # 飽和度
            hue=0.01                # 色相
        ),
        transforms.GaussianBlur(kernel_size=3)
    ])

    for i in range(num_variants):
        aug_img = transform(img)
        aug_img.save(os.path.join(output_dir, f'variant_{i+1:02d}.jpg'))


if __name__ == '__main__':
    # # # # # 預設參數 # # # # #
    generate_variants('input.jpg')

    # # # # # 自訂參數 # # # # #
    # generate_variants('input.jpg', output_dir='output', num_variants=100, degrees=5, bleed=5)
