document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  const courseSelect = document.getElementById("course-select");
  const assignmentList = document.getElementById("assignment-list");
  const btnCreate = document.getElementById("btn-create");

  // Load danh sách khóa học
  fetch("http://localhost:5000/api/teacher/courses", {
    headers: { "Authorization": "Bearer " + token }
  })
    .then(res => res.json())
    .then(data => {
      data.courses.forEach(course => {
        const option = document.createElement("option");
        option.value = course.id;
        option.textContent = `${course.id} - ${course.name}`;
        courseSelect.appendChild(option);
      });
    });

  // Khi chọn khóa học thì load bài tập
  courseSelect.addEventListener("change", loadAssignments);

  // Tạo bài tập mới
  btnCreate.addEventListener("click", () => {
    const courseId = courseSelect.value;
    if (!courseId) return alert("Vui lòng chọn khóa học!");

    const title = prompt("Tên bài tập:");
    const description = prompt("Mô tả:");
    const deadline = prompt("Hạn nộp (YYYY-MM-DDTHH:MM):");

    if (!title || !deadline) return;

    fetch("http://localhost:5000/api/teacher/assignments", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({ title, description, deadline, course_id: courseId })
    })
      .then(res => res.json())
      .then(data => {
        alert(data.message);
        loadAssignments(); // reload bài tập mới
      });
  });

  // Hàm load danh sách bài tập theo khóa học
  function loadAssignments() {
    const courseId = courseSelect.value;
    assignmentList.innerHTML = "";

    if (!courseId) return;

    fetch(`http://localhost:5000/api/teacher/assignments?course_id=${courseId}`, {
      headers: {
        "Authorization": "Bearer " + token
      }
    })
      .then(res => res.json())
      .then(data => {
        if (!Array.isArray(data.assignments)) return;

        data.assignments.forEach(ass => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${ass.title}</td>
            <td>${ass.course_name}</td>
            <td>${ass.deadline || "Không có"}</td>
            <td>
              <button onclick="editAssignment(${ass.id})">Sửa</button>
              <button onclick="deleteAssignment(${ass.id})">Xóa</button>
            </td>
          `;
          assignmentList.appendChild(row);
        });
      });
  }
});

// Hàm sửa bài tập (placeholder)
function editAssignment(id) {
  alert("Sửa bài tập ID: " + id);
}

// Hàm xóa bài tập
function deleteAssignment(id) {
  const token = localStorage.getItem("token");
  if (!confirm("Bạn có chắc muốn xóa bài tập này?")) return;

  fetch(`http://localhost:5000/api/teacher/assignments/${id}`, {
    method: "DELETE",
    headers: {
      "Authorization": "Bearer " + token
    }
  })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      location.reload();
    });
}

document.getElementById("course-select").addEventListener("change", () => {
  const courseId = document.getElementById("course-select").value;
  const token = localStorage.getItem("token");

  fetch(`http://localhost:5000/api/teacher/courses/${courseId}/details`, {
    headers: { Authorization: "Bearer " + token }
  })
    .then(res => res.json())
    .then(data => {
      const lessonDiv = document.getElementById("lesson-list");
      const assignmentDiv = document.getElementById("assignment-list");

      // Bài học
      lessonDiv.innerHTML = "<h3>📘 Bài học:</h3>";
      data.lessons.forEach(l => {
        lessonDiv.innerHTML += `<p>🔹 ${l.title}</p>`;
      });

      // Bài tập
      assignmentDiv.innerHTML = "<h3>📚 Bài tập:</h3>";
      data.assignments.forEach(a => {
        assignmentDiv.innerHTML += `<p>📝 ${a.title} - Hạn: ${a.deadline || "Không có"}</p>`;
      });
    });
});
