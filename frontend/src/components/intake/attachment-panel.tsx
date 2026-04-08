export function AttachmentPanel({
  attachments,
  onUpload,
}: {
  attachments: Array<{ fileName: string; caption: string }>;
  onUpload: (file: File) => void;
}) {
  return (
    <section className="rounded-[24px] border border-white/10 bg-white/5 p-4">
      <h2 className="text-[21px] font-semibold text-white">图片附件</h2>
      <input
        accept="image/png,image/jpeg,image/webp"
        aria-label="上传参考图片"
        className="mt-3 block w-full text-sm text-white/80 file:mr-4 file:rounded-full file:border-0 file:bg-white file:px-4 file:py-2 file:text-sm file:text-black"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) onUpload(file);
        }}
        type="file"
      />
      <div className="mt-3 space-y-2">
        {attachments.map((item) => (
          <div key={item.fileName} className="rounded-[18px] bg-black/25 p-3 text-sm text-white/78">
            {item.fileName}
            {item.caption ? ` - ${item.caption}` : ""}
          </div>
        ))}
      </div>
    </section>
  );
}
