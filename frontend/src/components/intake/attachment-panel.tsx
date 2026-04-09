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
        <div className="grid gap-3 sm:grid-cols-2">
          {attachments.map((item) => (
            <div
              key={`${item.file_name}-${item.created_at ?? item.id ?? "pending"}`}
              className="overflow-hidden rounded-[22px] border border-white/10 bg-black/24"
            >
              {item.preview_url ? (
                <div className="aspect-[4/3] bg-black/50">
                  <img
                    alt={`${item.file_name} 缩略图`}
                    className="h-full w-full object-cover"
                    src={item.preview_url}
                  />
                </div>
              ) : (
                <div className="flex aspect-[4/3] items-center justify-center bg-white/5 px-4 text-center text-[12px] tracking-[0.08em] text-white/36">
                  暂无预览
                </div>
              )}
              <div className="space-y-1 px-3 py-3">
                <p className="truncate text-[13px] font-medium text-white/86">{item.file_name}</p>
                {item.caption ? (
                  <p className="text-[12px] leading-[1.55] text-white/46">
                    {item.caption}
                  </p>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
