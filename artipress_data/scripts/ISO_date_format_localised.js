document.querySelectorAll("time.localised-date").forEach(el => {
    const raw = el.getAttribute("datetime");
    if (!raw) return;

    const date = new Date(raw);
    if (isNaN(date)) return;

    const datePart = date.toLocaleDateString(undefined, {
        day:   "numeric",
        month: "long",
        year:  "numeric",
    });

    const timePart = date.toLocaleTimeString(undefined, {
        hour:   "2-digit",
        minute: "2-digit",
    });

    el.textContent = `${datePart} at ${timePart}`;
});