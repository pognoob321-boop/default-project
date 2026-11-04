"""CLI entrypoint for ai-clipper."""

import click
from pathlib import Path

from .downloader import download_video
from .transcriber import transcribe
from .analyzer import detect_highlights
from .output import save_clips


@click.command()
@click.argument("url")
@click.option("--clips", "-n", default=5, help="Number of clips to generate")
@click.option("--max-length", "-l", default=60, help="Max clip length in seconds")
@click.option("--output", "-o", default="output", help="Output directory")
@click.option("--model", "-m", default="base", help="Whisper model size (tiny/base/small/medium/large)")
@click.option("--horizontal", is_flag=True, help="Keep original aspect ratio (default: vertical 9:16)")
def main(url: str, clips: int, max_length: int, output: str, model: str, horizontal: bool):
    """AI Video Clipper — YouTube URL in, short-form clips out."""

    output_dir = Path(output)
    work_dir = output_dir / ".work"

    click.echo(f"Downloading video...")
    dl = download_video(url, work_dir)
    click.echo(f"  Title: {dl['title']}")
    click.echo(f"  Duration: {dl['duration']:.0f}s")

    click.echo(f"Transcribing with whisper ({model})...")
    transcript = transcribe(dl["audio_path"], model_size=model)
    click.echo(f"  Language: {transcript['language']}")
    click.echo(f"  Segments: {len(transcript['segments'])}")

    click.echo(f"Detecting highlights...")
    highlights = detect_highlights(
        transcript,
        num_clips=clips,
        max_length=max_length,
    )
    click.echo(f"  Found {len(highlights)} highlights")

    click.echo(f"Clipping and saving...")
    saved = save_clips(
        video_path=dl["video_path"],
        highlights=highlights,
        title=dl["title"],
        output_dir=output_dir,
        vertical=not horizontal,
    )

    click.echo(f"\nDone! {len(saved)} clips saved to {output_dir}/")
    for clip in saved:
        click.echo(f"  {clip['clip']}.mp4 ({clip['duration']}s, score: {clip['score']}/10)")
        click.echo(f"    {clip['reason']}")


if __name__ == "__main__":
    main()
