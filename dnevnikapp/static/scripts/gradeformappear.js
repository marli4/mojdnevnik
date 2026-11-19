document.addEventListener("DOMContentLoaded", () => {
    const gradeModal = document.getElementById("gradeModal");
    const absenceModal = document.getElementById("absenceModal");

    let currentStudent = null;

    //grade
    document.querySelectorAll(".lessongrade").forEach(button => {
        button.addEventListener("click", () => {
            currentStudent = button.dataset.student;
            gradeModal.style.display = "flex";
        });
    });

    gradeModal.querySelectorAll("[data-grade]").forEach(button => {
        button.addEventListener("click", () => {
            const grade = button.dataset.grade;
            updateGrade(currentStudent, grade);
            closeModal(gradeModal);
        });
    });

    //absence
    document.querySelectorAll(".lessonabsence").forEach(button => {
        button.addEventListener("click", () => {
            currentStudent = button.dataset.student;
            absenceModal.style.display = "flex";
        });
    });


    absenceModal.querySelectorAll("[data-absence]").forEach(button => {
        button.addEventListener("click", () => {
            const absence = button.dataset.absence;
            updateAbsence(currentStudent, absence);
            closeModal(absenceModal);
        });
    });

    document.querySelectorAll(".modal-close").forEach(button => {
        button.addEventListener("click", () => {
            closeModal(button.closest(".lesson-modal"));
        });
    });

    document.querySelectorAll(".lesson-modal").forEach(modal => {
        modal.addEventListener("click", event => {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            closeModal(gradeModal);
            closeModal(absenceModal);
        }
    });

    function updateGrade(studentId, grade) {
        const button = document.querySelector(
            `.lessongrade[data-student="${studentId}"]`
        );

        const input = document.querySelector(
            `input[name="grade_${studentId}"]`
        );

        input.value = grade;
        button.textContent = grade || "";
        button.dataset.value = grade;

        button.classList.remove("grade-good", "grade-ok", "grade-bad");

        if (grade >= 4) {
            button.classList.add("grade-good");
        } else if (grade == 3) {
            button.classList.add("grade-ok");
        } else if (grade == 2) {
            button.classList.add("grade-bad");
        }
    }

    function updateAbsence(studentId, absence) {
        const button = document.querySelector(
            `.lessonabsence[data-student="${studentId}"]`
        );

        const input = document.querySelector(
            `input[name="absence_${studentId}"]`
        );

        input.value = absence;
        button.textContent = absence;
        button.dataset.value = absence;

        button.classList.remove("absence", "absence-excused");

        if (absence === "УП") {
            button.classList.add("absence-excused");
        } else if (absence === "Н") {
            button.classList.add("absence");
        }
    }

    function closeModal(modal) {
        modal.style.display = "none";
    }
});