document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");

  fetch("http://localhost:5000/api/teacher/profile", {
    headers: {
      "Authorization": "Bearer " + token
    }
  })
  .then(res => res.json())
  .then(data => {
    const card = document.querySelector(".course-card");
    card.innerHTML = `
      <p><strong>Tên:</strong> ${data.fullname}</p>
      <p><strong>Email:</strong> ${data.email}</p>
      <p><strong>Bộ môn:</strong> ${data.department || "Chưa cập nhật"}</p>
      <p><strong>Ngày tham gia:</strong> ${data.joined_date || "Chưa có"}</p>
    `;
  })
  .catch(err => {
    alert("Không thể tải hồ sơ!");
    console.error(err);
  });
});