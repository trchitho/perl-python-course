async function loadComponents() {
  const slots = document.querySelectorAll('[data-component]');
  await Promise.all(Array.from(slots).map(async slot => {
    const name = slot.getAttribute('data-component');
    try {
      const res = await fetch(`/frontend/components/${name}.html`);
      const html = await res.text();
      slot.innerHTML = html;
      // Sidebar needs dynamic links based on role; inline scripts in components don't run via innerHTML
      if (name === 'Sidebar') {
        try {
          const sideNav = slot.querySelector('#sideLinks');
          if (sideNav) {
            const role = (localStorage.getItem('role') || 'student').toLowerCase();
            const link = (href, text) => `<a href="${href}">${text}</a>`;
            if (role === 'teacher') {
              sideNav.innerHTML = [
                link('/frontend/pages/teacher/dashboard.html','📊 Dashboard'),
                link('/frontend/pages/teacher/courses.html','📚 Courses'),
                link('/frontend/pages/teacher/lessons.html','📘 Lessons'),
                link('/frontend/pages/teacher/quizzes.html','📝 Quizzes'),
                link('/frontend/pages/teacher/grades.html','📑 Grades'),
                link('/frontend/pages/teacher/subscribers.html','👥 Subscribers'),
                link('/frontend/pages/teacher/announcements.html','🔔 Announcements')
              ].join('');
            } else if (role === 'admin') {
              sideNav.innerHTML = [
                link('/frontend/pages/admin/dashboard.html','📊 Dashboard'),
                link('/frontend/pages/admin/users.html','👤 Users'),
                link('/frontend/pages/admin/enrollments.html','🧾 Enrollments'),
                link('/frontend/pages/admin/logs.html','🗂 Logs'),
                link('/frontend/pages/admin/settings.html','⚙️ Settings')
              ].join('');
            } else {
              sideNav.innerHTML = [
                link('/frontend/pages/student/dashboard.html','📊 Dashboard'),
                link('/frontend/pages/student/courses.html','📚 Courses'),
                link('/frontend/pages/student/lessons.html','📘 Lessons'),
                link('/frontend/pages/student/quiz.html','📝 Quiz'),
                link('/frontend/pages/student/quiz-history.html','📒 Quiz History'),
                link('/frontend/pages/student/progress.html','📈 Progress'),
                link('/frontend/pages/student/chatbot.html','🤖 Chatbot'),
                link('/frontend/pages/student/profile.html','👤 Profile')
              ].join('');
            }
          }
        } catch (e) { /* ignore */ }
      }
    } catch (e) {
      slot.innerHTML = `<!-- Failed to load component ${name} -->`;
    }
  }));
  // Ensure top navigation behavior is loaded after components are injected
  try {
    if (!window.__topnavLoaded) {
      const s = document.createElement('script');
      s.src = '/frontend/assets/topnav.js';
      s.onload = () => { window.__topnavLoaded = true; };
      document.head.appendChild(s);
    }
  } catch (e) { /* ignore */ }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadComponents);
} else {
  loadComponents();
}
