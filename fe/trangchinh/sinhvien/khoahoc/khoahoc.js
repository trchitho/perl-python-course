const token = localStorage.getItem("token");

fetch("http://localhost:5000/api/student/all-courses", {
  method: "GET",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token
  }
})
.then(response => {
  if (!response.ok) {
    throw new Error("Không thể lấy danh sách khóa học: " + response.status);
  }
  return response.json();
})
.then(data => {
  if (!Array.isArray(data)) {
    console.error("Dữ liệu trả về không phải mảng:", data);
    return;
  }

  const courseGrid = document.querySelector(".course-grid");
  courseGrid.innerHTML = ""; // clear cũ nếu có

  data.forEach(course => {
    const card = document.createElement("div");
    card.className = "course-card";
    card.innerHTML = `
    <h3>${course.name}</h3>
    <div class="teacher">Giảng viên: ${course.teacher_name}</div>
    <p>${course.description}</p>
    <p style="color: ${course.enrolled ? 'green' : 'red'}">
      ${course.enrolled ? "Đã đăng ký" : "Chưa đăng ký"}
    </p>
    <button onclick="xemChiTiet(${course.id})">Xem chi tiết</button>
    ${!course.enrolled ? `<button onclick="enroll(${course.id})">Đăng ký</button>` : ""}
  `;
    courseGrid.appendChild(card);
  });
})
.catch(error => {
  console.error("Lỗi khi gọi API:", error);
});

function xemChiTiet(courseId) {
  window.location.href = `../khoahoc/chi-tiet-khoahoc.html?id=${courseId}`;
}

function enroll(courseId) {
  fetch("http://localhost:5000/api/student/enroll", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ course_id: courseId })
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
    location.reload(); // reload lại để cập nhật trạng thái "Đã đăng ký"
  })
  .catch(err => {
    alert("Đăng ký thất bại");
    console.error(err);
  });
}
