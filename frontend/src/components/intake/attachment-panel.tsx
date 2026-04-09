import type { SessionAttachment } from "../../lib/types";

export function AttachmentPanel({
  attachments,
  disabled,
  onUpload,
}: {
  attachments: SessionAttachment[];
  disabled: boolean;
  onUpload: (file: File) => void;
}) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <p className="text-[12px] uppercase tracking-[0.2em] text-white/40">参考附件</p>
        <input
          accept="image/png,image/jpeg,image/webp"
          aria-label="上传参考图片"
          className="block max-w-[220px] text-[12px] text-white/72 file:mr-3 file:rounded-full file:border-0 file:bg-white file:px-3 file:py-1.5 file:text-[12px] file:text-black disabled:opacity-40"
          disabled={disabled}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) {
              onUpload(file);
              event.currentTarget.value = "";
            }
          }}
          type="file"
        />
      </div>
      {attachments.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {attachments.map((item) => (
            <div
              key={`${item.file_name}-${item.created_at ?? item.id ?? "pending"}`}
              className="rounded-full border border-white/10 bg-white/6 px-3 py-1.5 text-[12px] text-white/76"
            >
              {item.file_name}
              {item.caption ? ` · ${item.caption}` : ""}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
