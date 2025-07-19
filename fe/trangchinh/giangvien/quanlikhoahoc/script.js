document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");

  fetch("http://localhost:5000/api/teacher/courses", {
    headers: {
      "Authorization": "Bearer " + token
    }
  })
  .then(res => res.json())
  .then(data => {
    const list = document.getElementById("course-list");
    list.innerHTML = ""; // Clear nếu reload
    data.courses.forEach(course => {
      const div = document.createElement("div");
      div.className = "course-card";
      div.innerHTML = `
        <h3>${course.name}</h3>
        <p>${course.description || "Không có mô tả"}</p>
        <small>Ngày tạo: ${course.created_at || "Không rõ"}</small><br>
        <button onclick="location.href='dsbaihoc.html?course_id=${course.id}'">Danh sách</button>
        <button onclick="editCourse(${course.id})">Chỉnh sửa</button>
        <button onclick="deleteCourse(${course.id})">Xoá</button>
      `;
      list.appendChild(div);
    });
  })
  .catch(err => {
    console.error("Lỗi khi lấy danh sách khóa học:", err);
  });
});

// Tạo khóa học mới
document.getElementById("create-course-form").addEventListener("submit", function (e) {
  e.preventDefault();
  const token = localStorage.getItem("token");
  const name = document.getElementById("course-name").value;
  const description = document.getElementById("course-description").value;

  fetch("http://localhost:5000/api/teacher/courses", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify({ name, description })
  })
    .then(res => res.json())
    .then(data => {
      alert("✅ " + data.message);
      location.reload(); // Reload để cập nhật danh sách
    })
    .catch(err => {
      alert("❌ Không thể tạo khóa học");
      console.error(err);
    });
});

// Chỉnh sửa khóa học
function editCourse(courseId) {
  const newName = prompt("Nhập tên khóa học mới:");
  if (!newName) return;
  const newDescription = prompt("Nhập mô tả mới:");

  const token = localStorage.getItem("token");

  fetch(`http://localhost:5000/api/teacher/courses/${courseId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify({ name: newName, description: newDescription })
  })
    .then(res => res.json())
    .then(data => {
      alert("✅ " + data.message);
      location.reload();
    })
    .catch(err => {
      alert("❌ Lỗi khi cập nhật khóa học");
      console.error(err);
    });
}

// Xóa khóa học
function deleteCourse(courseId) {
  const confirmed = confirm("Bạn có chắc muốn xóa khóa học này?");
  if (!confirmed) return;

  const token = localStorage.getItem("token");

  fetch(`http://localhost:5000/api/teacher/courses/${courseId}`, {
    method: "DELETE",
    headers: {
      "Authorization": "Bearer " + token
    }
  })
    .then(res => res.json())
    .then(data => {
      alert("🗑️ " + data.message);
      location.reload();
    })
    .catch(err => {
      alert("❌ Lỗi khi xoá khóa học");
      console.error(err);
    });
}
