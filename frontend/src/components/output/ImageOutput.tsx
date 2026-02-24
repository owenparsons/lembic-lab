interface ImageOutputProps {
  data: Record<string, unknown>;
}

export function ImageOutput({ data }: ImageOutputProps) {
  if ("image/png" in data) {
    const src = `data:image/png;base64,${data["image/png"] as string}`;
    return (
      <img
        src={src}
        alt="Plot output"
        className="max-w-full rounded"
        loading="lazy"
      />
    );
  }

  if ("image/svg+xml" in data) {
    return (
      <div
        className="max-w-full [&>svg]:max-w-full"
        dangerouslySetInnerHTML={{ __html: data["image/svg+xml"] as string }}
      />
    );
  }

  if ("image/jpeg" in data) {
    const src = `data:image/jpeg;base64,${data["image/jpeg"] as string}`;
    return (
      <img
        src={src}
        alt="Plot output"
        className="max-w-full rounded"
        loading="lazy"
      />
    );
  }

  return null;
}
