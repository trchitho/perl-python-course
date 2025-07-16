document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");

  // Load danh sách khóa học vào <select>
  fetch("http://localhost:5000/api/teacher/courses", {
    headers: {
      "Authorization": "Bearer " + token
    }
  })
  .then(res => res.json())
  .then(data => {
    const select = document.getElementById("course");
    const uploadSelect = document.getElementById("upload-course-id");

    data.courses.forEach(course => {
      const option = document.createElement("option");
      option.value = course.id;
      option.textContent = `${course.id} - ${course.name}`;
      select.appendChild(option);

      const option2 = option.cloneNode(true);
      uploadSelect.appendChild(option2);
    });
  });

  // Xử lý tạo bài học
  document.getElementById("lesson-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const token = localStorage.getItem("token");
    const title = document.getElementById("lesson_name").value;
    const content = document.getElementById("description").value;
    const course_id = document.getElementById("course").value;

    fetch("http://localhost:5000/api/teacher/lessons", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({ title, content, course_id })
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById("success-message").style.display = "block";
      document.getElementById("lesson-preview").style.display = "block";

      document.getElementById("preview-name").textContent = title;
      document.getElementById("preview-desc").textContent = content;
      document.getElementById("preview-course").textContent = course_id;
    })
    .catch(err => {
      alert("❌ Lỗi khi tạo bài học");
      console.error(err);
    });
  });
});
