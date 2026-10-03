interface TimelineItem {
  id: number | string;
  title: string;
  detail?: string;
  time?: string;
}

// 时间线：审计记录、整改记录等追溯链
export function TimelineList({ items }: { items: TimelineItem[] }) {
  if (items.length === 0) return <div className="empty">暂无记录</div>;
  return <div className="table">
    {items.map((item) => <article key={item.id} className="row">
      <strong>{item.title}</strong>
      <span>{item.detail ?? ""}</span>
      <span>{item.time ?? ""}</span>
    </article>)}
  </div>;
}
