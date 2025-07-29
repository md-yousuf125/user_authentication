from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import mysql.connector
import bcrypt
import smtplib

PORT = 8000

# MySQL connection details
db_config = {
    "host": "localhost",
    "user": "root",         # Your MySQL username
    "password": "yousuf125@", # Your MySQL password
    "database": "auth_system"
}

def send_email(to_email, username):
    sender_email = "md2004y@gmail.com"
    sender_password = "----------------"

    subject = "Registration Successful"
    body = f"Hello {username},\n\nYour registration was successful!"

    message = f"Subject: {subject}\n\n{body}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message)
        server.quit()
        print("📧 Email sent successfully!")
    except Exception as e:
        print("❌ Email sending failed:", e)

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/login.html"

        try:
            if self.path.endswith(".css"):
                with open(self.path.strip("/"), "rb") as file:
                    self.send_response(200)
                    self.send_header("Content-type", "text/css")
                    self.end_headers()
                    self.wfile.write(file.read())
            else:
                with open(self.path.strip("/"), "rb") as file:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")


    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode('utf-8'))

        username = post_data.get("username", [""])[0]
        email = post_data.get("email", [""])[0]
        password = post_data.get("password", [""])[0]

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if self.path == "/register":
            try:
                cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                               (username, email, hashed_pw))
                conn.commit()
                send_email(email, username)

                # Redirect to success page
                self.send_response(302)
                self.send_header("Location", "/register_success.html")
                self.end_headers()

            except mysql.connector.Error:
                # Redirect to error page if duplicate or DB issue
                self.send_response(302)
                self.send_header("Location", "/error.html")
                self.end_headers()

            finally:
                cursor.close()
                conn.close()

        elif self.path == "/login":
            cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
                # Redirect to success page
                self.send_response(302)
                self.send_header("Location", "/login_success.html")
                self.end_headers()
            else:
                # Redirect to error page
                self.send_response(302)
                self.send_header("Location", "/error.html")
                self.end_headers()
httpd = HTTPServer(("localhost", PORT), RequestHandler)
print(f"🚀 Server running on http://localhost:{PORT}")
httpd.serve_forever()

