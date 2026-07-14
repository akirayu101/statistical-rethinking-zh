document.addEventListener("click", async (event) => {
  const button = event.target.closest(".copy-code");
  if (!button) return;

  const listing = button.closest(".code-listing");
  const code = listing?.querySelector("pre:not(.code-output) > code");
  if (!code) return;

  const originalLabel = button.textContent;
  try {
    let copied = false;
    if (navigator.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(code.textContent);
        copied = true;
      } catch {
        copied = false;
      }
    }
    if (!copied) {
      const fallback = document.createElement("textarea");
      fallback.value = code.textContent;
      fallback.setAttribute("readonly", "");
      fallback.style.position = "fixed";
      fallback.style.opacity = "0";
      document.body.append(fallback);
      fallback.select();
      if (!document.execCommand("copy")) throw new Error("copy command failed");
      fallback.remove();
    }
    button.textContent = "已复制";
  } catch {
    button.textContent = "复制失败";
  }
  window.setTimeout(() => {
    button.textContent = originalLabel;
  }, 1400);
});
