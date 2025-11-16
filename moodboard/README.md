Moodboard - Información sensible

Quick summary

This folder contains a printable moodboard for your storytelling project `Información sensible` by Carlos A. Aceves. Open `index.html` in a browser to view and print to PDF (File → Print → Save as PDF).

Files

- index.html — moodboard layout with 9 slides.
- style.css — styles including suggested palette and fonts.
- content.json — structured text for each slide (editable).

How to customize

1. Replace cover image: in `index.html` replace the div with id `cover-img` with an <img> tag pointing to your asset, for example:

```html
<img src="images/mi-portada.jpg" alt="Portada de Información sensible" style="width:100%;height:auto;border-radius:6px;">
```
2. Change colors: update hex values in `style.css` `.swatch` classes and other styles.
3. Change fonts: index.html links to Google Fonts. Replace with your chosen fonts.
4. Add images: add <img> elements to each `.slide` or create a grid of thumbnails.

Quick preview (optional):

From the `moodboard` folder you can run a simple HTTP server for a nicer preview:

```bash
python3 -m http.server 8000
# then open http://localhost:8000 in your browser
```

Viewing `historia.json` as a read page:

If you want to view the story as a readable web page, open the new `historia.html` in the project root. If you run the server from the project root, then open:

http://localhost:8000/historia.html

The page reuses the moodboard look and loads content from `historia.json`.

Export to PDF

- Chrome/Chromium: Open `index.html`, press Ctrl+P, choose "Save as PDF". Under "More settings", uncheck "Headers and footers" if desired. Set margins to "Default" or "None".
- Firefox: similar. For macOS choose Print -> PDF -> Save as PDF.

Image assets and licensing

- Use Unsplash or Pexels for free high-quality photos. Suggested keywords: "portrait intimate", "documentary photography", "warm light street", "hands close up".
- For icons use Feather Icons (feathericons.com) or Heroicons.

Deliverable suggestions

- PDF of moodboard (export from browser)
- Upload to Canva and replicate your elements using the suggested fonts and color codes
- Add the final file to your course as a PDF or a shared link (Canva, Miro, Milanote)

Notes & assumptions

- Assumed storytelling: "Información sensible" - a project for emotional connections about social themes. If you have a different project title or topic, replace titles and narrative to match.

Next steps

- Replace placeholders with your images and finalize copy for each slide.
- If you want, I can assemble a more visual version using Canva templates, or generate a PDF file for you if you provide images.
