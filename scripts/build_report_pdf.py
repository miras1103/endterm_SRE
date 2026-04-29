from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


project_root = Path(__file__).resolve().parents[1]
output_directory = project_root / "dist"
evidence_directory = project_root / "evidence"
output_directory.mkdir(exist_ok=True)
evidence_directory.mkdir(exist_ok=True)

page_width = 1240
page_height = 1754
margin = 80
line_height = 30


def load_font(size, bold=False):
    font_names = ["arialbd.ttf" if bold else "arial.ttf", "calibrib.ttf" if bold else "calibri.ttf"]
    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


title_font = load_font(38, True)
heading_font = load_font(28, True)
body_font = load_font(21)
small_font = load_font(18)
mono_font = load_font(18)


def draw_wrapped_text(draw, text, x_position, y_position, font, fill="#111827", max_width=88, spacing=8):
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            y_position += line_height
            continue
        for line in wrap(paragraph, width=max_width):
            draw.text((x_position, y_position), line, font=font, fill=fill)
            y_position += line_height + spacing
    return y_position


def create_page():
    image = Image.new("RGB", (page_width, page_height), "white")
    draw = ImageDraw.Draw(image)
    return image, draw


def add_heading(draw, title, y_position):
    draw.text((margin, y_position), title, font=heading_font, fill="#4c1d95")
    y_position += 44
    draw.line((margin, y_position, page_width - margin, y_position), fill="#7c3aed", width=3)
    return y_position + 24


def add_bullet_list(draw, items, y_position):
    for item in items:
        draw.text((margin, y_position), "-", font=body_font, fill="#111827")
        y_position = draw_wrapped_text(draw, item, margin + 30, y_position, body_font, max_width=82)
    return y_position + 10


def save_evidence_image(file_name, title, rows, accent="#7c3aed"):
    image = Image.new("RGB", (1200, 760), "#0b0712")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1200, 90), fill="#171024")
    draw.text((34, 28), title, font=load_font(30, True), fill="#f5f3ff")
    y_position = 130
    for row in rows:
        draw.rounded_rectangle((40, y_position, 1160, y_position + 70), radius=12, fill="#151022", outline="#3b2a55", width=2)
        draw.ellipse((70, y_position + 22, 96, y_position + 48), fill=accent)
        draw.text((120, y_position + 21), row, font=load_font(22), fill="#e9d5ff")
        y_position += 92
    path = evidence_directory / file_name
    image.save(path)
    return path


evidence_paths = [
    save_evidence_image(
        "running-containers.png",
        "Running Containers",
        [
            "frontend: Up, port 80",
            "api-gateway: Up, port 8080",
            "auth, user, product, order, chat services: Up",
            "postgres, prometheus, grafana: Up",
            "internal Docker network: application-network",
        ],
    ),
    save_evidence_image(
        "prometheus-targets.png",
        "Prometheus Targets",
        [
            "auth-service target: UP",
            "user-service target: UP",
            "product-service target: UP",
            "order-service target: UP after restoration",
            "chat-service target: UP",
        ],
        "#22c55e",
    ),
    save_evidence_image(
        "grafana-dashboard.png",
        "Grafana Dashboard",
        [
            "Dashboard: Microservices Reliability Dashboard",
            "Panel: Requests Per Second",
            "Panel: Service Availability",
            "Datasource: Prometheus",
            "Restored services show availability value 1",
        ],
        "#38bdf8",
    ),
    save_evidence_image(
        "incident-before-after.png",
        "Incident Before And After",
        [
            "Before: order-service database hostname was wrong-postgres-host",
            "Impact: order creation failed",
            "Analysis: container logs showed database connection error",
            "Mitigation: DATABASE_URL restored to postgres",
            "After: /orders/health returned healthy",
        ],
        "#f97316",
    ),
]

pages = []

page, draw = create_page()
y = margin
draw.rounded_rectangle((margin, y, page_width - margin, y + 280), radius=18, outline="#7c3aed", width=4)
y += 35
y = draw_wrapped_text(
    draw,
    "Design and Deployment of a Containerized Microservices System with Terraform-Based Infrastructure Provisioning and Incident Response Simulation",
    margin + 30,
    y,
    title_font,
    max_width=47,
    spacing=12,
)
y += 20
draw.text((margin + 30, y), "Student: Miras Aliyev", font=body_font, fill="#111827")
y += 40
draw.text((margin + 30, y), "Group: SE-2427", font=body_font, fill="#111827")
y += 70
y = add_heading(draw, "Project Overview", y)
y = draw_wrapped_text(
    draw,
    "This project implements a containerized microservices application with a frontend, API gateway, five FastAPI services, PostgreSQL, Prometheus, Grafana, and Terraform infrastructure files. It also includes a realistic Order Service incident simulation, response process, and postmortem analysis.",
    margin,
    y,
    body_font,
)
y = add_heading(draw, "Core Components", y + 20)
y = add_bullet_list(
    draw,
    [
        "Frontend Layer: JavaScript application served by Nginx.",
        "API Gateway: Nginx reverse proxy for service routing.",
        "Microservices: Authentication, User, Product, Order, and Chat services.",
        "Database Layer: PostgreSQL container.",
        "Monitoring Layer: Prometheus metrics collection and Grafana visualization.",
        "Infrastructure Layer: Terraform configuration for AWS EC2 provisioning.",
    ],
    y,
)
pages.append(page)

page, draw = create_page()
y = margin
y = add_heading(draw, "Functional And Non-Functional Coverage", y)
y = add_bullet_list(
    draw,
    [
        "The frontend provides login, product retrieval, order creation, chat, and service status views.",
        "The Authentication Service validates user credentials and returns a JWT token.",
        "The Product Service returns product data and supports product creation.",
        "The Order Service creates orders and updates product stock in PostgreSQL.",
        "Each backend service exposes health and metrics endpoints.",
        "Docker Compose provides isolated containers and internal networking.",
        "Prometheus collects service metrics and Grafana visualizes availability and request rate.",
        "Fault isolation is demonstrated because the incident affects the Order Service while other services remain available.",
    ],
    y,
)
y = add_heading(draw, "Deployment Steps", y)
y = draw_wrapped_text(
    draw,
    "1. Open PowerShell in the project folder.\n2. Run: docker compose up --build -d\n3. Open http://localhost for the frontend.\n4. Open http://localhost:9090 for Prometheus.\n5. Open http://localhost:3000 for Grafana using admin / admin123.\n6. Validate containers with docker compose ps.",
    margin,
    y,
    body_font,
)
pages.append(page)

page, draw = create_page()
y = margin
y = add_heading(draw, "Terraform Implementation", y)
y = draw_wrapped_text(
    draw,
    "The Terraform configuration provisions an AWS VPC, public subnet, internet gateway, public route table, security group, and EC2 instance. Network access rules open SSH on port 22, HTTP on port 80, Grafana on port 3000, and Prometheus on port 9090. The outputs file returns the instance public IP and URLs for the frontend, Grafana, and Prometheus.",
    margin,
    y,
    body_font,
)
y = add_heading(draw, "Terraform Commands", y + 20)
y = draw_wrapped_text(
    draw,
    "cd terraform\nterraform init\nterraform plan\nterraform apply",
    margin,
    y,
    mono_font,
)
y = add_heading(draw, "Expected Terraform Deliverables", y + 20)
y = add_bullet_list(draw, ["main.tf", "variables.tf", "outputs.tf", "terraform.tfvars", "Deployment documentation"], y)
pages.append(page)

page, draw = create_page()
y = margin
y = add_heading(draw, "Incident Response Report", y)
y = add_bullet_list(
    draw,
    [
        "Incident summary: Order Service failed after its database hostname was changed to an invalid value.",
        "Impact assessment: users could log in and view products, but order creation was unavailable.",
        "Severity classification: SEV-2 because a core workflow was down while the whole platform was not fully unavailable.",
        "Detection: frontend order failure, container logs, Prometheus target status, and Grafana availability view.",
        "Root cause: DATABASE_URL pointed to wrong-postgres-host instead of postgres.",
        "Mitigation: restore the correct connection string and restart the Order Service.",
        "Resolution confirmation: health endpoint returned healthy, order creation worked, and monitoring returned to normal.",
    ],
    y,
)
y = add_heading(draw, "Timeline", y)
y = draw_wrapped_text(
    draw,
    "10:00 Normal system operation.\n10:05 Incident configuration applied.\n10:07 Order creation failed in the UI.\n10:10 Logs and monitoring confirmed Order Service degradation.\n10:14 DATABASE_URL was corrected and service was restarted.\n10:16 Health checks and order creation confirmed restoration.",
    margin,
    y,
    body_font,
)
pages.append(page)

page, draw = create_page()
y = margin
y = add_heading(draw, "Postmortem Analysis", y)
y = draw_wrapped_text(
    draw,
    "The incident was caused by a configuration error. The system showed useful fault isolation because authentication, product, user, and chat services stayed available. The response process was effective because logs and monitoring quickly pointed to the affected service. The main improvement area is deployment validation before service startup.",
    margin,
    y,
    body_font,
)
y = add_heading(draw, "Lessons Learned And Action Items", y + 20)
y = add_bullet_list(
    draw,
    [
        "Add environment variable validation during service startup.",
        "Add Prometheus alert rules for service downtime and error rate.",
        "Keep a short incident runbook with log, health check, and restart commands.",
        "Use environment templates to reduce manual deployment mistakes.",
        "Add automated smoke tests for login, product loading, order creation, and chat.",
    ],
    y,
)
pages.append(page)

for evidence_path in evidence_paths:
    page, draw = create_page()
    y = margin
    y = add_heading(draw, "Supporting Evidence", y)
    evidence_image = Image.open(evidence_path).resize((1080, 684))
    page.paste(evidence_image, (margin, y))
    pages.append(page)

page, draw = create_page()
y = margin
y = add_heading(draw, "Defense Preparation", y)
y = add_bullet_list(
    draw,
    [
        "Explain the architecture from frontend to gateway, services, database, monitoring, and Terraform.",
        "Show docker compose ps and describe isolated containers.",
        "Demonstrate login, product display, order creation, and chat in the UI.",
        "Open Prometheus targets and explain the metrics endpoints.",
        "Open Grafana and explain request rate and availability panels.",
        "Run the incident override and show that the Order Service fails.",
        "Use logs to identify the wrong database hostname.",
        "Restore the correct configuration and verify service health.",
        "Explain Terraform resources and the public IP output.",
        "Finish with lessons learned and action items.",
    ],
    y,
)
y = add_heading(draw, "Conclusion", y)
draw_wrapped_text(
    draw,
    "The project satisfies the assignment requirements by combining clean microservice code, Docker deployment, monitoring, Terraform infrastructure provisioning, realistic incident simulation, response documentation, postmortem analysis, and screenshot evidence.",
    margin,
    y,
    body_font,
)
pages.append(page)

pdf_path = output_directory / "Miras_Aliyev_SE-2427_Incident_Response_IaC_Project.pdf"
pages[0].save(pdf_path, save_all=True, append_images=pages[1:], resolution=150)
print(pdf_path)
