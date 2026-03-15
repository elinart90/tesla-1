/* VRA FMS – File Upload Page JS */

document.addEventListener('DOMContentLoaded', function () {
  var dropZone = document.getElementById('dropZone');
  var fileInput = document.querySelector('#dropZone input[type="file"]');
  var filePreview = document.getElementById('filePreview');
  var previewName = document.getElementById('previewName');
  var previewSize = document.getElementById('previewSize');
  var previewIcon = document.getElementById('previewIcon');
  var removeBtn = document.getElementById('removeFile');
  var fileNameInput = document.getElementById('id_file_name');
  var submitBtn = document.getElementById('submitBtn');
  var submitText = document.getElementById('submitText');
  var submitSpinner = document.getElementById('submitSpinner');
  var form = document.getElementById('uploadForm');

  function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  function getFileIcon(ext) {
    var icons = {
      pdf: '📄', doc: '📝', docx: '📝', xls: '📊', xlsx: '📊',
      ppt: '📑', pptx: '📑', jpg: '🖼️', jpeg: '🖼️', png: '🖼️',
      txt: '📃', zip: '🗜️'
    };
    return icons[ext.toLowerCase()] || '📎';
  }

  function showPreview(file) {
    var ext = file.name.split('.').pop();
    if (previewIcon) previewIcon.textContent = getFileIcon(ext);
    if (previewName) previewName.textContent = file.name;
    if (previewSize) previewSize.textContent = formatFileSize(file.size);
    if (filePreview) filePreview.style.display = 'flex';
    // Auto-fill filename field
    if (fileNameInput && !fileNameInput.value) {
      fileNameInput.value = file.name;
    }
  }

  function clearPreview() {
    if (filePreview) filePreview.style.display = 'none';
    if (fileInput) fileInput.value = '';
    if (fileNameInput) fileNameInput.value = '';
  }

  // File input change
  if (fileInput) {
    fileInput.addEventListener('change', function () {
      if (fileInput.files && fileInput.files[0]) {
        showPreview(fileInput.files[0]);
      }
    });
  }

  // Drag & Drop
  if (dropZone) {
    dropZone.addEventListener('dragover', function (e) {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', function () {
      dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', function (e) {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      var files = e.dataTransfer.files;
      if (files.length > 0 && fileInput) {
        // Transfer files to input
        var dataTransfer = new DataTransfer();
        dataTransfer.items.add(files[0]);
        fileInput.files = dataTransfer.files;
        showPreview(files[0]);
      }
    });

    // Click on drop zone opens file dialog
    dropZone.addEventListener('click', function (e) {
      if (fileInput && !e.target.closest('input')) {
        fileInput.click();
      }
    });
  }

  // Remove file button
  if (removeBtn) {
    removeBtn.addEventListener('click', clearPreview);
  }

  // Form submit – show spinner
  if (form && submitBtn) {
    form.addEventListener('submit', function () {
      if (submitText) submitText.style.display = 'none';
      if (submitSpinner) submitSpinner.style.display = 'inline-block';
      if (submitBtn) submitBtn.disabled = true;
    });
  }
});
