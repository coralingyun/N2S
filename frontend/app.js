const healthStatus = document.getElementById("healthStatus");
const novelInput = document.getElementById("novelInput");
const yamlOutput = document.getElementById("yamlOutput");
const statusMessage = document.getElementById("statusMessage");
const errorMessage = document.getElementById("errorMessage");

const loadSampleButton = document.getElementById("loadSampleButton");
const convertButton = document.getElementById("convertButton");
const validateButton = document.getElementById("validateButton");
const copyButton = document.getElementById("copyButton");
const downloadButton = document.getElementById("downloadButton");

function setStatus(message) {
  statusMessage.textContent = message;
}

function setError(message) {
  if (!message) {
    errorMessage.hidden = true;
    errorMessage.textContent = "";
    return;
  }
  errorMessage.hidden = false;
  errorMessage.textContent = message;
}

function setButtonLoading(button, isLoading, loadingText) {
  if (!button.dataset.defaultText) {
    button.dataset.defaultText = button.textContent;
  }
  button.disabled = isLoading;
  button.textContent = isLoading ? loadingText : button.dataset.defaultText;
}

function countLikelyChapters(text) {
  const matches = text.match(/^\s*(?:第\s*[零〇一二三四五六七八九十百千两\d]+\s*章(?:\s+.*)?|Chapter\s+\d+(?:\s*[:：.\-]\s*.*)?)\s*$/gim);
  return matches ? matches.length : 0;
}

function requireYaml() {
  const yaml = yamlOutput.value.trim();
  if (!yaml) {
    setError("请先生成或粘贴 YAML 内容。");
    return null;
  }
  return yaml;
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const text = await response.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch (error) {
    data = { message: text || `请求失败：${response.status}` };
  }
  if (!response.ok) {
    const detail = data.detail || data;
    const message = detail.message || data.message || `请求失败：${response.status}`;
    const errors = detail.errors || data.errors || [];
    throw new Error(formatErrors(message, errors));
  }
  return data;
}

function formatErrors(message, errors) {
  if (!errors || errors.length === 0) {
    return message;
  }
  const lines = errors.map((item) => `${item.path || "$"}: ${item.reason || "校验失败"}`);
  return `${message}\n${lines.join("\n")}`;
}

async function checkHealth() {
  try {
    const data = await requestJson("/health");
    healthStatus.textContent = data.status === "ok" ? "后端可用" : "后端状态未知";
    healthStatus.className = "status-pill status-ok";
  } catch (error) {
    healthStatus.textContent = "后端不可用";
    healthStatus.className = "status-pill status-bad";
    setError("无法连接后端服务，请确认 FastAPI 已启动。");
  }
}

async function loadSampleNovel() {
  setError("");
  setStatus("正在加载示例小说...");
  setButtonLoading(loadSampleButton, true, "加载中...");
  try {
    const data = await requestJson("/sample-novel");
    novelInput.value = data.text;
    setStatus("示例小说已加载。");
  } catch (error) {
    setError(error.message);
    setStatus("示例小说加载失败。");
  } finally {
    setButtonLoading(loadSampleButton, false);
  }
}

async function convertNovel() {
  const inputText = novelInput.value.trim();
  if (!inputText) {
    setError("请输入小说文本。");
    return;
  }
  const chapterCount = countLikelyChapters(inputText);
  if (chapterCount < 3) {
    setError(`小说文本至少需要 3 个章节；当前识别到 ${chapterCount} 个章节。`);
    setStatus("无法生成：章节数量不足。");
    return;
  }

  setError("");
  setStatus("正在生成剧本 YAML...");
  setButtonLoading(convertButton, true, "生成中...");
  try {
    const data = await requestJson("/convert", {
      method: "POST",
      body: JSON.stringify({ input_text: inputText }),
    });
    yamlOutput.value = data.yaml || "";
    setStatus("剧本 YAML 已生成。");
  } catch (error) {
    setError(error.message);
    setStatus("生成失败。");
  } finally {
    setButtonLoading(convertButton, false);
  }
}

async function validateYaml() {
  const yaml = requireYaml();
  if (!yaml) return;

  setError("");
  setStatus("正在校验 YAML...");
  setButtonLoading(validateButton, true, "校验中...");
  try {
    const data = await requestJson("/validate", {
      method: "POST",
      body: JSON.stringify({ yaml_text: yaml }),
    });
    if (data.ok) {
      setStatus("YAML Schema 校验通过。");
    } else {
      setStatus("YAML Schema 校验失败。");
      setError(formatErrors(data.message || "YAML Schema 校验失败。", data.errors || []));
    }
  } catch (error) {
    setError(error.message);
    setStatus("校验失败。");
  } finally {
    setButtonLoading(validateButton, false);
  }
}

async function copyYaml() {
  const yaml = requireYaml();
  if (!yaml) return;

  setError("");
  setButtonLoading(copyButton, true, "复制中...");
  try {
    await navigator.clipboard.writeText(yaml);
    setStatus("YAML 已复制到剪贴板。");
  } catch (error) {
    try {
      yamlOutput.select();
      document.execCommand("copy");
      setStatus("YAML 已复制到剪贴板。");
    } catch (fallbackError) {
      setError("复制失败，请手动选择输出区内容后复制。");
      setStatus("复制失败。");
    }
  } finally {
    setButtonLoading(copyButton, false);
  }
}

function downloadYaml() {
  const yaml = requireYaml();
  if (!yaml) return;

  setError("");
  setButtonLoading(downloadButton, true, "下载中...");
  const blob = new Blob([yaml], { type: "application/x-yaml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "screenplay.yaml";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  setStatus("screenplay.yaml 已开始下载。");
  setButtonLoading(downloadButton, false);
}

loadSampleButton.addEventListener("click", loadSampleNovel);
convertButton.addEventListener("click", convertNovel);
validateButton.addEventListener("click", validateYaml);
copyButton.addEventListener("click", copyYaml);
downloadButton.addEventListener("click", downloadYaml);

checkHealth();
