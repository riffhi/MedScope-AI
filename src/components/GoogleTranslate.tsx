// // src/components/GoogleTranslate.tsx
// import React, { useEffect } from "react";
// import "./GoogleTranslate.css"; // We will create this CSS file next

// const GoogleTranslate = () => {
//   // This function is the callback that the Google script will run
//   const googleTranslateElementInit = () => {
//     new (window as any).google.translate.TranslateElement(
//       {
//         pageLanguage: "en",
//         includedLanguages: "en,hi,bn,te,ta", // English, Hindi, Bengali, Telugu, Tamil
//         layout: (window as any).google.translate.TranslateElement.InlineLayout.SIMPLE,
//         autoDisplay: false,
//       },
//       "google_translate_element" // The ID of the hidden div in index.html
//     );
//   };

//   // This function handles changes from our custom dropdown
//   const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
//     // Find the dropdown that Google creates
//     const googleCombo = document.querySelector(".goog-te-combo") as HTMLSelectElement;
//     if (googleCombo) {
//       googleCombo.value = e.target.value;
//       // Tell Google's script that the language has changed
//       googleCombo.dispatchEvent(new Event("change"));
//     }
//   };

//   useEffect(() => {
//     // This adds the initialization function to the window object
//     // so the Google script can call it.
//     (window as any).googleTranslateElementInit = googleTranslateElementInit;
//   }, []);

//   return (
//     <div className="translator-wrapper">
//       <select
//         id="custom-translator-select"
//         onChange={handleLanguageChange}
//         defaultValue="en"
//         aria-label="Select language"
//       >
//         <option value="en">English</option>
//         <option value="hi">हिन्दी (Hindi)</option>
//         <option value="bn">বাংলা (Bengali)</option>
//         <option value="te">తెలుగు (Telugu)</option>
//         <option value="ta">தமிழ் (Tamil)</option>
//       </select>
//     </div>
//   );
// };

// export default GoogleTranslate;