document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");

  fetch("http://localhost:5000/api/teacher/report-summary", {
    headers: {
      "Authorization": "Bearer " + token
    }
  })
  .then(res => res.json())
  .then(data => {
    document.querySelector(".progress-bar-inner").style.width = data.completion_rate + "%";
    document.querySelector(".progress-bar-inner").textContent = data.completion_rate + "%";

    document.querySelector(".avg-score").textContent = (data.completion_rate / 10).toFixed(1); // giả lập điểm trung bình

    const completeText = `${data.on_time_count}/${data.total_students} sinh viên`;
    document.querySelector(".item:nth-child(3) p").textContent = completeText;
  })
  .catch(err => {
    alert("❌ Không thể tải dữ liệu báo cáo học tập!");
    console.error(err);
  });
});
