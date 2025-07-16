document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");

  fetch("http://localhost:5000/api/student/courses", {
    headers: { "Authorization": "Bearer " + token }
  })
    .then(res => res.json())
    .then(courses => {
      const select = document.getElementById("course-select");
      courses.forEach(course => {
        const option = document.createElement("option");
        option.value = course.id;
        option.textContent = course.name;
        select.appendChild(option);
      });
    });
});

function submitFeedback() {
  const token = localStorage.getItem("token");
  const courseId = document.getElementById("course-select").value;
  const message = document.getElementById("message").value;

  if (!courseId || !message) {
    alert("Vui lòng chọn khóa học và nhập nội dung đánh giá.");
    return;
  }

  fetch("http://localhost:5000/api/student/feedback", {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ course_id: courseId, message: message })
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("response").textContent = data.message;
      document.getElementById("message").value = "";
    })
    .catch(err => {
      document.getElementById("response").textContent = "❌ Lỗi khi gửi đánh giá.";
    });
}
