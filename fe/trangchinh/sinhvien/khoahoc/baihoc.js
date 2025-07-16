const params = new URLSearchParams(window.location.search);
const lessonId = params.get("lesson_id");
const token = localStorage.getItem("token");

fetch(`http://localhost:5000/api/student/lesson/${lessonId}`, {
  headers: {
    "Authorization": "Bearer " + token
  }
})
  .then(response => {
    if (!response.ok) throw new Error("Không thể lấy bài học: " + response.status);
    return response.json();
  })
  .then(data => {
    document.getElementById("lesson-title").textContent = data.title;
    document.getElementById("lesson-content").innerHTML = `<p>${data.content}</p>`;

    // 👇 Nếu có bài tập trắc nghiệm thì hiển thị
    if (data.quiz) {
      const quizContainer = document.createElement("div");
      quizContainer.className = "quiz-section";
      quizContainer.innerHTML = `
        <h2>📝 Bài tập trắc nghiệm</h2>
        <pre style="background:#f4f4f4;padding:10px;border-radius:8px;">${data.quiz}</pre>
        <button onclick="window.location.href='baitap.html?lesson_id=${lessonId}'">Làm bài tập</button>
      `;
      document.getElementById("lesson-content").appendChild(quizContainer);
    }
  })
  .catch(error => {
    console.error("Lỗi khi gọi API:", error);
  });


  document.addEventListener("DOMContentLoaded", () => {
  const startQuizBtn = document.getElementById("start-quiz-btn");
  if (startQuizBtn) {
    startQuizBtn.addEventListener("click", () => {
      window.location.href = `baitap.html?lesson_id=${lessonId}`;
    });
  }
});