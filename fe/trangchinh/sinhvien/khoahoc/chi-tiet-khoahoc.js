document.addEventListener("DOMContentLoaded", () => {
  const courseId = new URLSearchParams(window.location.search).get("id");
  const token = localStorage.getItem("token");

  if (!token || !courseId) {
    alert("Không có token hoặc ID khóa học!");
    return;
  }

  fetch(`http://localhost:5000/api/student/course-detail/${courseId}`, {
    method: "GET",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error("Không thể tải dữ liệu khóa học: " + response.status);
      }
      return response.json();
    })
    .then(data => {
      // Hiển thị thông tin khóa học
      document.getElementById("course-title").textContent = `📘 ${data.name}`;
      document.getElementById("course-desc").textContent = data.description;

      // Hiển thị danh sách bài học
      const lessonList = document.getElementById("lesson-list");
      lessonList.innerHTML = "";

      data.lessons.forEach(lesson => {
        const lessonCard = document.createElement("div");
        lessonCard.className = "card";
        lessonCard.innerHTML = `
          <h3>${lesson.title}</h3>
          <button onclick="window.location.href='baihoc.html?lesson_id=${lesson.id}'">Xem bài học</button>
        `;
        lessonList.appendChild(lessonCard);
      });
    })
    .catch(error => {
      console.error("Lỗi:", error);
    });
});
