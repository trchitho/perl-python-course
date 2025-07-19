document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");

  // Load danh sách khóa học vào các <select>
  fetch("http://localhost:5000/api/teacher/courses", {
    headers: { "Authorization": "Bearer " + token }
  })
    .then(res => res.json())
    .then(data => {
      const selects = [
        document.getElementById("course"),
        document.getElementById("upload-course-id")
      ];
      data.courses.forEach(course => {
        selects.forEach(select => {
          if (select) {
            const opt = document.createElement("option");
            opt.value = course.id;
            opt.textContent = `${course.id} - ${course.name}`;
            select.appendChild(opt);
          }
        });
      });
    });

  // Xử lý upload ảnh chèn vào nội dung
  const imageInput = document.getElementById("image-upload");
  if (imageInput) {
    imageInput.addEventListener("change", async function (e) {
      const file = e.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("image", file);

      try {
        const res = await fetch("http://localhost:5000/api/teacher/upload-image", {
          method: "POST",
          body: formData
        });
        const data = await res.json();

        if (data && data.image_url) {
          const contentTextarea = document.getElementById("content");
          contentTextarea.value += `<img src="${data.image_url}" alt="Ảnh đính kèm">`;
        } else {
          alert("❌ Upload ảnh thất bại!");
        }
      } catch (err) {
        console.error(err);
        alert("❌ Lỗi khi upload ảnh");
      }
    });
  }

  // Submit tạo bài học
  const lessonForm = document.getElementById("lesson-form");
  if (lessonForm) {
    lessonForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const title = document.getElementById("lesson_name").value.trim();
      const content = document.getElementById("content").value.trim();
      const course_id = document.getElementById("course").value;

      if (!title || !content || !course_id) {
        alert("❗ Vui lòng điền đầy đủ thông tin bài học.");
        return;
      }

      fetch("http://localhost:5000/api/teacher/lessons", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ title, content, course_id })
      })
        .then(res => {
          if (res.status === 201) return res.json();
          throw new Error("Tạo bài học thất bại!");
        })
        .then(data => {
          const successMsg = document.getElementById("success-message");
          if (successMsg) {
            successMsg.textContent = "✅ " + data.message;
            successMsg.style.display = "block";
            setTimeout(() => { successMsg.style.display = "none"; }, 3000);
          }

          // Hiển thị preview
          document.getElementById("lesson-preview").style.display = "block";
          document.getElementById("preview-name").textContent = title;
          document.getElementById("preview-desc").innerHTML = content;
          document.getElementById("preview-course").textContent = course_id;

          this.reset();
        })
        .catch(err => {
          console.error(err);
          alert("❌ Lỗi khi tạo bài học");
        });
    });
  }

  // Submit upload từ file
  const uploadForm = document.getElementById("upload-form");
  if (uploadForm) {
    uploadForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(this);

      fetch("http://localhost:5000/api/teacher/upload-lesson-from-file", {
        method: "POST",
        headers: { "Authorization": "Bearer " + token },
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          const successMsg = document.getElementById("success-message");
          if (data.message && successMsg) {
            successMsg.textContent = "✅ " + data.message;
            successMsg.style.display = "block";
            setTimeout(() => { successMsg.style.display = "none"; }, 3000);
            this.reset();
          } else {
            alert("❌ " + (data.error || "Có lỗi xảy ra khi upload bài học"));
          }
        })
        .catch(err => {
          console.error(err);
          alert("❌ Lỗi mạng khi upload bài học");
        });
    });
  }
});
