# Use an official Python runtime as a parent image
FROM python:3.11

WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install streamlit pandas numpy plotly

# Copy the rest of the working directory contents into the container at /app
COPY . /app

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run app.py when the container launches
CMD streamlit run house.py