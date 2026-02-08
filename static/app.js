// Bootstrap validation + loading spinner + autofill demo
(function () {
    const form = document.getElementById("churnForm");
    const spinner = document.getElementById("loadingSpinner");
    const btnSubmit = document.getElementById("btnSubmit");
  
    const btnAutofill = document.getElementById("btnAutofill");
    const btnClear = document.getElementById("btnClear");
  
    function setValue(name, value) {
      const el = document.querySelector(`[name="${name}"]`);
      if (!el) return;
      el.value = value;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }
  
    // Contoh data realistis (bisa kamu ubah)
    const demo = {
      CreditScore: 650,
      Geography: "Germany",
      Gender: "Female",
      Age: 44,
      Tenure: 6,
      Balance: 125000.50,
      NumOfProducts: 2,
      HasCrCard: 1,
      IsActiveMember: 0,
      EstimatedSalary: 120000.00
    };
  
    btnAutofill?.addEventListener("click", () => {
      Object.entries(demo).forEach(([k, v]) => setValue(k, v));
      // animasi kecil
      form?.classList.remove("pulse");
      void form?.offsetWidth;
      form?.classList.add("pulse");
    });
  
    btnClear?.addEventListener("click", () => {
      form?.reset();
      form?.classList.remove("was-validated");
    });
  
    // Validation + spinner
    form?.addEventListener("submit", (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      } else {
        // show spinner
        spinner?.classList.remove("d-none");
        btnSubmit?.setAttribute("disabled", "disabled");
      }
      form.classList.add("was-validated");
    });
  })();
  
  // Add a pulse animation class dynamically via CSS injection (simple)
  (function(){
    const style = document.createElement("style");
    style.textContent = `
      .pulse { animation: pulseGlow .45s ease; }
      @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 rgba(122,167,255,0.0); }
        50% { box-shadow: 0 0 0.75rem rgba(122,167,255,0.22); }
        100% { box-shadow: 0 0 0 rgba(122,167,255,0.0); }
      }
    `;
    document.head.appendChild(style);
  })();
  