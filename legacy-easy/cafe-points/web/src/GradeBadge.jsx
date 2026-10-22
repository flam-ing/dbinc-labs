export default function GradeBadge(props) {
  var color = props.grade == "VIP" ? "gold" : "gray";
  return <span style={{ color: color }}>{props.grade}</span>;
}
