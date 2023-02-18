# blog_fullstack
Fullstack blog app using Flask and Bootstrap

# Setup
1. Install dependencies with ```pip install requirements.txt```
2. Setup MySQL config in data.py
3. Run ```python3 main.py```

# MySQL tables
users(id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR, username VARCHAR, password VARCHAR)

blogs(id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR, body VARCHAR, title VARCHAR, author VARCHAR, body TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

# Demo
<img width="1438" alt="Screenshot 2023-02-18 at 18 09 01" src="https://user-images.githubusercontent.com/92104549/219854932-fb21ff20-114e-4f8e-87f6-425ef89a4cfa.png">
<img width="1438" alt="Screenshot 2023-02-18 at 18 14 36" src="https://user-images.githubusercontent.com/92104549/219854946-eaf1d5d0-351c-402d-ab10-2e104d8020e0.png">
