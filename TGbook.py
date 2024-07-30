import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from fpdf import FPDF
import base64
from streamlit import selectbox
from io import BytesIO
import tempfile

# Set the app to wide mode
st.set_page_config(layout="wide")

# Function to inject custom CSS for gradient background
def inject_css():
    st.markdown(
        """
        <style>
        .main {
            background: linear-gradient(60Deg,#D3F3EF,#9FE7F5, #D39FF5,#FC7ECC,#ff0477 );
            padding: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )



# Function to display the start page with clickable cards
def show_start_page():
    inject_css()  # Inject the CSS for the gradient background
    st.title("TG Book 📊💻")
    st.write(
        "Welcome to the TG Book Dashboard. Click on the sections below to view details:"
    )

    # Create a grid layout for the cards
    col1, col2 = st.columns(2)

    # Define colors
    color_class = "#FFB6C1"  # Light pink
    color_student = "#FFFF99"  # Light yellow
    color_notes = "#98FB98"  # Pale green
    color_timetable = "#ADD8E6"  # Light blue

    # Function to create styled buttons with different colors
    def styled_button(label, color, page_name):
        button_clicked = st.button(label, key=page_name)
        if button_clicked:
            st.session_state.page = page_name.lower().replace(" ", "_")
            

    # Display styled buttons in columns
    with col1:
        styled_button("Class Performance", color_class, "class_performance")
        styled_button("Student Performance", color_student, "student_performance")

    with col2:
        styled_button("Notes", color_notes, "notes")
        styled_button("Time Table", color_timetable, "time_table")

    # Add space for bottom placement
    st.markdown("<br>", unsafe_allow_html=True)

    # Add hyperlinks at the center bottom
    st.markdown(
        "<div style='text-align: center; padding-top: 20px;'>Developed by <a href='https://www.linktr.ee/aryandhone555'>ARYAN</a> | <a href='https://www.linkedin.com/in/aryandhone555'>LinkedIn</a> | <a href='mailto:er.aryandhone@gmail.com'>Email</a></div>",
        unsafe_allow_html=True,
    )


# Function to display the Notes page
def show_notes():
    inject_css()
    st.header("Notes Editor")

    # Create or verify the Notes folder
    notes_dir = "Notes"
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)

    # Text editor to create and save notes
    new_note = st.text_area("Write your note below", height=200)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Note"):
            if new_note.strip():
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                note_filename = f"note_{timestamp}.txt"
                note_filepath = os.path.join(notes_dir, note_filename)
                with open(note_filepath, "w") as f:
                    f.write(new_note)
                st.success("Note saved successfully.")
                st.session_state.new_note = ""  # Clear the text editor
                ###st.experimental_rerun()  # Refresh the page to show the new note
            else:
                st.error("Note content is empty.")
    with col2:
        if st.button("Clear Note"):
            st.session_state.new_note = ""
            ###st.experimental_rerun()  # Refresh the page to clear the text editor

    # List all existing notes sorted by time and date
    notes_files = sorted(
        [f for f in os.listdir(notes_dir) if f.endswith(".txt")],
        key=lambda x: os.path.getmtime(os.path.join(notes_dir, x)),
        reverse=True,
    )

    # Display existing notes content as separate cards with delete button
    st.header("Existing Notes")
    for note_file in notes_files:
        note_file_path = os.path.join(notes_dir, note_file)
        with open(note_file_path, "r") as f:
            note_content = f.read()
        st.markdown(f"### {note_file}")
        st.text_area(
            note_file, value=note_content, height=200, key=note_file, disabled=True
        )

        # Delete button for each note
        delete_button = st.button(f"Delete {note_file}", key=f"delete_{note_file}")
        if delete_button:
            os.remove(note_file_path)
            st.success(f"Note {note_file} deleted successfully.")
            ###st.experimental_rerun()  # Refresh the page to update the notes list

    # Back to home button
    if st.button("Back to Home"):
        st.session_state.page = "home"
        ###st.experimental_rerun()


# Function to display the Time Table page
def show_time_table():
    inject_css()
    st.header("Time Table")
    timetable_image_path = "timetable_image.jpg"  # Path to your timetable image
    timetable_image = open(timetable_image_path, "rb").read()
    st.image(timetable_image, use_column_width=True)
    if st.button("Back to Home"):
        st.session_state.page = "home"
        ###st.experimental_rerun()


# Function to display the Class Performance page
def show_class_performance():
    inject_css()
    st.header("Class Performance")

    # Load the data
    data_path = "TGdatabase.csv"  # Change this to your CSV file path
    df = pd.read_csv(data_path)

    # Ensure the semester columns are numeric
    semesters = ["sem-I", "sem-II", "sem-III", "sem-IV", "sem-V"]
    df[semesters] = df[semesters].apply(pd.to_numeric, errors="coerce")

    # Calculate average CGPA for each semester
    avg_cgpa = df[semesters].mean().reset_index()
    avg_cgpa.columns = ["Semester", "Average CGPA"]

    # Calculate highest and lowest CGPA for each semester
    highest_cgpa = df[semesters].max().reset_index()
    highest_cgpa.columns = ["Semester", "Highest CGPA"]

    lowest_cgpa = df[semesters].min().reset_index()
    lowest_cgpa.columns = ["Semester", "Lowest CGPA"]

    fig, ax = plt.subplots(figsize=(10, 5))  # Adjust figure size for a smaller graph

    # Plot the average CGPA
    bars = avg_cgpa.plot(
        kind="bar", x="Semester", y="Average CGPA", ax=ax, color="aqua", legend=False
    )

    # Add values on top of the bars
    for bar in bars.patches:
        ax.annotate(
            format(bar.get_height(), ".2f"),
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="center",
            size=10,
            xytext=(0, 8),
            textcoords="offset points",
        )

    # Plot the zigzag lines
    ax.plot(
        avg_cgpa["Semester"],
        avg_cgpa["Average CGPA"],
        color="yellow",
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=8,
        label="Average CGPA",
    )
    ax.plot(
        highest_cgpa["Semester"],
        highest_cgpa["Highest CGPA"],
        color="green",
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=8,
        label="Highest CGPA",
    )
    ax.plot(
        lowest_cgpa["Semester"],
        lowest_cgpa["Lowest CGPA"],
        color="red",
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=8,
        label="Lowest CGPA",
    )

    # Add values on top of the zigzag lines
    # for i, txt in enumerate(avg_cgpa['Average CGPA']):
    #     ax.annotate(format(txt, '.2f'), (i, txt), ha='center', va='bottom', fontsize=10, xytext=(0, 5), textcoords='offset points')

    for i, txt in enumerate(highest_cgpa["Highest CGPA"]):
        ax.annotate(
            format(txt, ".2f"),
            (i, txt),
            ha="center",
            va="bottom",
            fontsize=10,
            xytext=(0, 5),
            textcoords="offset points",
        )

    for i, txt in enumerate(lowest_cgpa["Lowest CGPA"]):
        ax.annotate(
            format(txt, ".2f"),
            (i, txt),
            ha="center",
            va="bottom",
            fontsize=10,
            xytext=(0, 5),
            textcoords="offset points",
        )

    ax.legend()

    st.pyplot(fig)

    # Display highest and lowest CGPA for each semester
    for semester in semesters:
        highest = df.loc[df[semester].idxmax()]
        lowest = df.loc[df[semester].idxmin()]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### Highest CGPA in {semester}")
            st.markdown(f"**Roll NO:** {highest['Roll NO']}")
            st.markdown(f"**Name:** {highest['Name of students']}")
            st.markdown(f"**CGPA:** {highest[semester]}")

        with col2:
            st.markdown(f"### Lowest CGPA in {semester}")
            st.markdown(f"**Roll NO:** {lowest['Roll NO']}")
            st.markdown(f"**Name:** {lowest['Name of students']}")
            st.markdown(f"**CGPA:** {lowest[semester]}")

    # Back to home button
    if st.button("Back to Home"):
        st.session_state.page = "home"
        ##st.experimental_rerun()


# Function to display the Student Performance page
def show_student_performance():
    inject_css()
    st.header("Student Performance")

    # Load the data
    data_path = "TGdatabase.csv"  # Change this to your CSV file path
    df = pd.read_csv(data_path)

    # Create a new column for display in dropdown
    df["Display Name"] = df.apply(
        lambda x: f"{x['Name of students']} -- {x['Roll NO']}", axis=1
    )

    # Dropdown for roll number selection
    roll_names = df["Display Name"].tolist()

    selection = st.selectbox("Enter/Select Name or Roll Number of the student:", roll_names, 0)

    if selection:
        # Extract roll number from selection
        selected_roll_number_str = selection.split("--")[-1].strip()

        # Find the corresponding row in the dataframe based on roll number string
        filtered_df = df[df["Display Name"].str.contains(selected_roll_number_str)]

        if not filtered_df.empty:
            student = filtered_df.iloc[0]  # Assuming there's only one match
            st.subheader(f"Performance Details for {student['Name of students']}")

            # Display additional student information
            gender = student["Gender"]  # Assuming 'Gender' column exists in your CSV
            if gender == "M":
                st.image("male.jpg", width=80)
            elif gender == "F":
                st.image("female.jpg", width=80)
            else:
                st.image(
                    "default.jpg", width=80
                )  # Default image if gender not specified

            st.markdown(f"**Roll Number:** {student['Roll NO']}")
            st.markdown(f"**PRN Number:** {student['PRN NO']}")
            st.markdown(f"**Student's Mobile Number:** {student.get('Students Mob. No', '')}")
            st.markdown(f"**Parent's Mobile Number:** {student.get('Parents Mob. No', '')}")
            st.markdown(f"**Student's mail ID:** {student.get('students mail id', '')}")
            st.markdown(f"**Parent's mail ID:** {student.get('parents mail id', '')}")
            st.markdown(f"**Permenant Address:** {student.get('Per. Address', '')}")
            st.markdown(f"**Residential Address:** {student.get('residential Address', '')}")

            # Line graph for performance across semesters
            semesters = ["sem-I", "sem-II", "sem-III", "sem-IV", "sem-V"]
            student_performance = student[semesters].values
            class_average = df[semesters].mean().values

            fig, ax = plt.subplots()
            ax.plot(
                semesters, student_performance, marker="o", label="Student Performance"
            )
            ax.plot(
                semesters,
                class_average,
                marker="o",
                linestyle="--",
                label="Class Average",
            )
            ax.set_xlabel("Semester")
            ax.set_ylabel("CGPA")
            ax.set_title(
                f'Performance Across Semesters for {student["Name of students"]}'
            )
            ax.legend()

            # Add values to the points on lines
            for x, y in zip(semesters, student_performance):
                ax.annotate(
                    f"{y:.2f}",
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 5),
                    ha="center",
                )

            for x, y in zip(semesters, class_average):
                ax.annotate(
                    f"{y:.2f}",
                    (x, y),
                    color="orange",
                    textcoords="offset points",
                    xytext=(0, 5),
                    ha="center",
                )

            st.pyplot(fig)

            # Add a download button for PDF
            download_filename = (
                f'{student["Roll NO"]}_{student["Name of students"]}.pdf' 
            )
            pdf_bytes = download_pdf(student)
            st.markdown(
                get_binary_file_downloader_html(
                    pdf_bytes,
                    download_filename,
                    f'Click here to download {student["Name of students"]}\'s Performance as PDF',
                ),
                unsafe_allow_html=True,
            )

            st.markdown("---")  # Divider between students

        else:
            st.warning(
                "No matching records found for the selected Name -- Roll Number."
            )

    # Back to home button
    if st.button("Back to Home"):
        st.session_state.page = "home"
        ##st.experimental_rerun()

# Function to download performance details as PDF

from fpdf import FPDF
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os

def download_pdf(student_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12, style="I")

    # Set colors
    pdf.set_fill_color(100, 176, 227)  # #5EB0FF
    pdf.set_draw_color(0, 0, 0)  # Black
    pdf.set_line_width(0.25)

    x1 = 10  # X-coordinate of the start point
    y1 = pdf.get_y() + 10  # Y-coordinate of the start point (current position + offset)
    x2 = 200  # X-coordinate of the end point
    y2 = y1  # Y-coordinate of the end point (same as start point for a horizontal line)
    pdf.line(x1, y1, x2, y2)

    b1 = (
        pdf.get_y() + 275
    )  # Y-coordinate of the start point (current position + offset)
    b2 = b1  # Y-coordinate of the end point (same as start point for a horizontal line)
    pdf.line(x1, b1, x2, b2)

    pdf.set_text_color(0, 0, 0)  # Black
    pdf.set_draw_color(252, 252, 252)  # Black
    pdf.set_line_width(0.5)

    # Add title
    pdf.set_font("Times", size=18, style="I")
    pdf.cell(0, 10, txt="Student Information", ln=True, align="C")
    pdf.ln(5)

    # Add data rows
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.set_font("Arial", size=12, style="I")
    fields = [
        ("Student Name:", str(student_data["Name of students"])),
        ("Roll Number:", str(student_data["Roll NO"])),
        ("PRN Number:", str(student_data["PRN NO"])),
        ("Student's Mobile Number:", str(student_data.get("Students Mob. No", ""))),
        ("Parent's Mobile Number:", str(student_data.get("Parents Mob. No", ""))),
        ("Student's mail ID:", str(student_data.get("students mail id", ""))),
        ("Parents' mail ID:", str(student_data.get("parents mail id", ""))),
        ("Permanent Address:", str(student_data.get("Per. Address", ""))),
        ("Residential Address:", str(student_data.get("residential Address", ""))),
    ]

    for field, value in fields:
        pdf.cell(60, 10, txt=field, border=1, ln=0, align="L", fill=True)
        pdf.cell(130, 10, txt=value, border=1, ln=1, align="C", fill=True)

    pdf.ln(10)  # Add some space after the table

    # Generate line graph as an image
    semesters = ["sem-I", "sem-II", "sem-III", "sem-IV", "sem-V"]
    student_performance = student_data[semesters].values

    # Load the data
    data_path = "TGdatabase.csv"  # Change this to your CSV file path
    df = pd.read_csv(data_path)
    class_average = df[semesters].mean().values

    fig, ax = plt.subplots()
    ax.plot(semesters, student_performance, marker="o", label="Student Performance")
    ax.plot(semesters, class_average, marker="o", linestyle="--", label="Class Average")
    ax.set_xlabel("Semester")
    ax.set_ylabel("CGPA")
    ax.set_title(f'Performance Across Semesters for {student_data["Name of students"]}')
    ax.legend()

    # Add values to the points on lines
    for x, y in zip(semesters, student_performance):
        ax.annotate(
            f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, 5), ha="center"
        )

    for x, y in zip(semesters, class_average):
        ax.annotate(
            f"{y:.2f}",
            (x, y),
            color="orange",
            textcoords="offset points",
            xytext=(0, 5),
            ha="center",
        )

    # Save the plot to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        plt.savefig(tmpfile, format="png")
        tmpfile_path = tmpfile.name
    plt.close(fig)

    # Embed the image into the PDF
    pdf.image(tmpfile_path, x=10, y=pdf.get_y(), w=180)
    

    # Add the hyperlink below the graph
    pdf.set_y(pdf.get_y() + 142)  # Adjust the Y position to below the image
    pdf.set_font("Arial", size=8)
    link = "https://www.linkedin.com/in/aryandhone555"
    text = "Created on TG_BOOK | by ARYAN"
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, text, 0, 0, "C", link=link)
    pdf.set_text_color(0, 0, 0)  # Reset text color to default

    # Save PDF to a BytesIO object
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)

    # Clean up the temporary file
    os.remove(tmpfile_path)

    return pdf_bytes




# function to generate link
def get_binary_file_downloader_html(bin_file, file_label="File", btn_label="Download"):
    """
    Generates a link to download a binary file.
    """
    b64 = base64.b64encode(bin_file.getvalue()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_label}">{btn_label}</a>'
    return href


# function to generate link
def get_binary_file_downloader_html(bin_file, file_label="File", btn_label="Download"):
    """
    Generates a link to download a binary file.
    """
    b64 = base64.b64encode(bin_file.getvalue()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_label}">{btn_label}</a>'
    return href


# Main function to control navigation
def main():
    st.session_state.setdefault("page", "home")  # Set default page as home

    # Render the appropriate page based on the session state
    if st.session_state.page == "home":
        show_start_page()
    elif st.session_state.page == "class_performance":
        show_class_performance()
    elif st.session_state.page == "student_performance":
        show_student_performance()
    elif st.session_state.page == "notes":
        show_notes()
    elif st.session_state.page == "time_table":
        show_time_table()


# Execute the main function to start the app
if __name__ == "__main__":
    main()
