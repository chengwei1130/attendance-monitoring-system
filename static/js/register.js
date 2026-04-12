// Preview uploaded image
document.getElementById('photo').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            console.log('Image selected:', file.name);
        };
        reader.readAsDataURL(file);
    }
});

// Auto-hide flash messages
setTimeout(() => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        flash.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => flash.remove(), 300);
    });
}, 5000);


const employmentType = document.getElementById("employment_type");
const salaryGroup = document.getElementById("salary-group");
const rateGroup = document.getElementById("rate-group");

function toggleFields() {
    const type = employmentType.value;

    if (type === "full_time") {
        salaryGroup.style.display = "block";
        rateGroup.style.display = "none";
        document.getElementById("hourly_rate").value = "";
    } else if (type === "part_time") {
        salaryGroup.style.display = "none";
        rateGroup.style.display = "block";
        document.getElementById("monthly_salary").value = "";

    } else {
        salaryGroup.style.display = "block";
        rateGroup.style.display = "block";
    }
}

// Run when dropdown changes
employmentType.addEventListener("change", toggleFields);

// Run once on page load (important!)
window.addEventListener("load", toggleFields);
