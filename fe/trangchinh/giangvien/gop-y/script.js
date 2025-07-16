document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");

  fetch("http://localhost:5000/api/teacher/feedbacks", {
    headers: {
      "Authorization": "Bearer " + token
    }
  })
  .then(res => res.json())
  .then(data => {
    const main = document.querySelector(".main");

    if (data.length === 0) {
      const p = document.createElement("p");
      p.textContent = "📭 Hiện chưa có góp ý nào.";
      main.appendChild(p);
    }

    data.forEach(fb => {
      const card = document.createElement("div");
      card.className = "course-card";
      card.innerHTML = `
        <p><strong>${fb.sender_name}</strong> (${fb.course_name})</p>
        <p>${fb.message}</p>
        <small>🕒 ${fb.created_at}</small>
      `;
      main.appendChild(card);
    });
  })
  .catch(err => {
    console.error("Lỗi khi lấy góp ý:", err);
  });
});