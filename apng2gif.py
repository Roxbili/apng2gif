import argparse
from pathlib import Path

import imageio
from PIL import Image
from loguru import logger


def _args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-dir", type=Path, default="apng_images", help="input apng file")
    parser.add_argument("-o", "--output-dir", type=Path, default="gif_images", help="output gif file")
    return parser.parse_args()


def apng2gif(apng_file, gif_file):

    # 使用 imageio 读取 APNG 文件
    reader = imageio.get_reader(apng_file, format="apng")

    frames = []
    durations = []
    for frame_num, frame in enumerate(reader):
        # 将每一帧转换为不透明背景的图像（白色背景）
        img = Image.fromarray(frame)

        # ------------------------
        # 白底背景
        # ------------------------
        # background = Image.new("RGBA", img.size, (255, 255, 255))  # 白色背景
        # background.paste(img, (0, 0), img)  # 组合背景与图像
        # frames.append(background.convert("RGB"))  # 转换为RGB去除透明度

        # ------------------------
        # 透明背景
        # ------------------------
        canvas = Image.new("RGBA", img.size, (255, 255, 255, 0))  # 透明背景
        canvas.paste(img, (0, 0), img)  # 将当前帧粘贴到透明背景上
        frames.append(canvas)

        meta_data = reader.get_meta_data(frame_num)
        durations.append(meta_data["duration"])

    # 将帧保存为 GIF，duration 控制每帧持续时间
    # disposal会让每一帧结束清空画布，避免重影
    frames[0].save(gif_file, save_all=True, append_images=frames[1:], duration=durations, loop=0, disposal=2)
    logger.info(f"convert {apng_file} to {gif_file}")


if __name__ == "__main__":
    args = _args()

    input_dir = Path(args.input_dir)
    assert input_dir.exists(), f"input dir {input_dir} not exist"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    for file in input_dir.glob("*.png"):
        apng_file = str(file)
        gif_file = str(output_dir / file.name.replace('.png', '.gif'))
        apng2gif(apng_file, gif_file)