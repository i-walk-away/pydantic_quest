(() => {
  const apiBase = "/api/v1/lessons";
  const tableBody = document.querySelector("[data-role='lesson-table']");
  const countLabel = document.querySelector("[data-role='count']");
  const message = document.querySelector("[data-role='message']");
  const messageText = document.querySelector("[data-role='message-text']");
  const refreshButton = document.querySelector("[data-action='refresh']");

  let lessons = [];

  const setMessage = (text, tone = "muted") => {
    message.classList.toggle("muted", tone === "muted");
    messageText.textContent = text;
  };

  const renderTable = () => {
    tableBody.innerHTML = "";
    lessons.forEach((lesson) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${lesson.order ?? ""}</td>
        <td>${lesson.slug ?? ""}</td>
        <td>${lesson.name ?? ""}</td>
        <td>${lesson.updated_at ? new Date(lesson.updated_at).toLocaleString() : "-"}</td>
        <td>
          <div class="actions">
            <a class="btn btn--ghost" href="./lesson.html?id=${lesson.id}">edit</a>
            <button class="btn btn--ghost" data-action="remove" data-id="${lesson.id}">delete</button>
          </div>
        </td>
      `;
      tableBody.appendChild(row);
    });
    countLabel.textContent = `${lessons.length} lessons`;
  };

  const loadLessons = async () => {
    setMessage("loading lessons...", "muted");
    try {
      const response = await fetch(`${apiBase}/get_all`);
      if (!response.ok) {
        throw new Error("failed to load lessons");
      }
      const data = await response.json();
      lessons = [...data].sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
      renderTable();
      setMessage("lessons loaded", "muted");
    } catch (error) {
      setMessage("failed to load lessons", "muted");
    }
  };

  const deleteLesson = async (lessonId) => {
    if (!lessonId) {
      return;
    }
    if (!window.confirm("Delete this lesson?")) {
      return;
    }

    setMessage("deleting...", "muted");
    try {
      const response = await fetch(`${apiBase}/${lessonId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("delete failed");
      }

      setMessage("lesson deleted", "muted");
      await loadLessons();
    } catch (error) {
      setMessage("delete failed", "muted");
    }
  };

  tableBody.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }
    const action = target.getAttribute("data-action");
    const lessonId = target.getAttribute("data-id");
    if (!action || !lessonId) {
      return;
    }

    if (action === "remove") {
      deleteLesson(lessonId);
    }
  });

  refreshButton.addEventListener("click", () => {
    loadLessons();
  });

  loadLessons();
})();
