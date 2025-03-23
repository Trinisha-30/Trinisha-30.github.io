document.getElementById('data-upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById('data-file');
  const file = fileInput.files[0];

  if (!file) {
    alert('Please select a file to upload.');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('/upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      alert('Failed to analyze file: ' + errorText);
      return;
    }

    const result = await response.json();
    displayResults(result);
  } catch (error) {
    console.error('Error during upload:', error);
    alert('An error occurred while uploading the file.');
  }
});

document.getElementById('clear-results').addEventListener('click', () => {
  document.getElementById('analysis-output').innerHTML = '<p>No data analyzed yet.</p>';
  document.getElementById('clear-results').style.display = 'none';
});

function displayResults(result) {
  const resultsDiv = document.getElementById('analysis-output');
  let html = '';

  // Report Title
  html += `<h3>Analysis Report</h3>`;

  // File Type and Basic Info
  html += `<p><strong>File Type:</strong> ${result.type}</p>`;
  if(result.type === "CSV" && result.row_count !== undefined) {
    html += `<p><strong>Row Count:</strong> ${result.row_count}</p>`;
  }

  // AI Analysis
  html += `<p><strong>AI Analysis:</strong> ${result.ai_flags}</p>`;

  // Vulnerabilities Section
  if(result.vulnerabilities && Array.isArray(result.vulnerabilities) && result.vulnerabilities.length > 0) {
    html += `<h4>Vulnerabilities Detected:</h4>`;
    html += `<ul>`;
    result.vulnerabilities.forEach(vuln => {
      html += `<li>${vuln}</li>`;
    });
    html += `</ul>`;
  } else {
    html += `<p><strong>Vulnerabilities Detected:</strong> None</p>`;
  }

  // Data Preview Section (formatted as a table)
  if(result.data_preview && Array.isArray(result.data_preview) && result.data_preview.length > 0) {
    html += `<h4>Data Preview (first ${result.data_preview.length} rows):</h4>`;
    html += `<table><thead><tr>`;
    const keys = Object.keys(result.data_preview[0]);
    keys.forEach(key => {
      html += `<th>${key}</th>`;
    });
    html += `</tr></thead><tbody>`;
    
    result.data_preview.forEach(row => {
      html += `<tr>`;
      keys.forEach(key => {
        html += `<td>${row[key]}</td>`;
      });
      html += `</tr>`;
    });
    
    html += `</tbody></table>`;
  } else {
    html += `<p>No data preview available.</p>`;
  }

  resultsDiv.innerHTML = html;
  document.getElementById('clear-results').style.display = 'inline-block';
}
