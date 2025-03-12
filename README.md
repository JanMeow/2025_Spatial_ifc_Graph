🚀 2025 Hackathon – "Find the Connection"


Introduction
Hey there!!! This repository contains two major components:

Find the Connection – Graph-based IFC processing & collision detection
Component Matching – AI-powered product search using a RAG (Retrieval-Augmented Generation) approach
This project is a continuation of my winning proposal from the 2025 Hackathon: "Find the Connection" 🏆.
Many features are still being actively developed, and I’d love to hear your feedback, suggestions, and contributions! 🚀

📌 Find the Connection – IFC to Graph Conversion & Collision Detection
This module converts an IFC model into a graph data structure that simultaneously acts as an AABB BVH tree (Broad-Phase Hierarchical Collision Detection).

Key Features
🔹 Corner Connection Analysis – Uses a DFS-based loop detection algorithm to verify if wall nodes can traverse back to themselves in 3-4 steps or arbitrary k-steps.
🔹 Broad-Phase Collision Detection – Uses Axis-Aligned Bounding Box (AABB) BVH trees for efficient intersection testing.
🔹 Narrow-Phase Collision Detection –GJK Algorithm (Gilbert-Johnson-Keerthi) for precise collision refinement.
🔹 Boolean Operations on Trimesh powered by Manifold3D for deeper geometric verification.
🔹 Visualization – Uses PyGlet for an interactive 3D mesh display.
🚧 Future Development
✅ Mid-Phase Collision Detection – Implementing Oriented Bounding Box (OOBB) testing.
✅ Separating Axis Theorem (SAT) Implementation – Just for fun, because why not? 😆
✅ Visualizing the graph on Neo4j

📌 Component Matching – AI-Driven Product Search
The Component Matching Catalog enables AI-powered retrieval & matching of construction components.

Key Features
🔹 RAG-Based Matching – Converts query + component catalog into vector embeddings.
🔹 Text Processing Pipeline

Extracts text from PDF catalogs (using PdfMiner).
Summarizes and extracts keywords using a language model (LLM).
Converts keywords into vector embeddings for similarity search.
🔹 Efficient Search & Retrieval – Stores embeddings in ChromaDB (vector database) for fast lookups.
🚧 Future Plans
✅ Segmentation Model for Visual Analysis – Extract visual details from PDFs for deeper insights.
✅ Graph Database Integration – Use Neo4j for structured querying, embedding connection data as an index.

⚠️ Important Note: Virtual Environments
Find the Connection and Component Matching use different Python virtual environments and have separate requirements.txt files.
Make sure to activate the correct environment before running the respective module:

bash
Kopieren
Bearbeiten
# Find the Connection
python -m venv venv_connection
source venv_connection/bin/activate  # (Linux/macOS)
venv_connection\Scripts\activate     # (Windows)
pip install -r requirements.txt

# Component Matching
python -m venv venv_matching
source venv_matching/bin/activate  # (Linux/macOS)
venv_matching\Scripts\activate     # (Windows)
pip install -r requirements_matching.txt
💡 Contributing & Feedback
This is an open-source project, and I’d love to get feedback from the community!
If you have any ideas, feature suggestions, or bug reports, feel free to:
🔹 Open an Issue 📌
🔹 Submit a Pull Request 💻
🔹 Reach out to me! 📩

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://github.com/JanMeow/2025_Spatial_ifc_Graph.git
git branch -M main
git push -uf origin main
```
# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.



## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.


## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
MIT license
## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
