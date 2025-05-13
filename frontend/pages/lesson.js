// lesson.js

document.addEventListener('DOMContentLoaded', () => {
    loadMenu();
    getLessonData();
    getCourseData();
});

function showLessonSection(sectionId) {
    document.getElementById('lesson-content-section').style.display = 'none';
    document.getElementById('lesson-quiz-section').style.display = 'none';

    const activeButtons = document.querySelectorAll('.lesson-navigation button.active');
    activeButtons.forEach(button => button.classList.remove('active'));

    const currentButton = document.querySelector(`.lesson-navigation button[onclick="showLessonSection('${sectionId}')"]`);
    if (currentButton) {
        currentButton.classList.add('active');
    }

    document.getElementById(`lesson-${sectionId}-section`).style.display = 'block';
}

function markLessonComplete() {
    if (currentLessonData && currentLessonData.quiz && !quizActive) {
        alert("Please complete the quiz before marking the lesson as complete.");
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const courseName = decodeURIComponent(urlParams.get('course'));
    const moduleTitle = decodeURIComponent(urlParams.get('module'));
    const lessonTitle = decodeURIComponent(urlParams.get('lesson'));

    const progressKey = `${courseName}_progress`;
    const savedProgress = JSON.parse(localStorage.getItem(progressKey)) || {};

    savedProgress[`${moduleTitle}_${lessonTitle}`] = true;
    localStorage.setItem(progressKey, JSON.stringify(savedProgress));
    console.log(`[Lesson.html] Progress updated in localStorage: ${localStorage.getItem(progressKey)}`);

    window.location.href = `Courses.html?course_name=${encodeURIComponent(courseName)}`;
}

function checkQuiz() {
    if (!currentLessonData || !currentLessonData.quiz || !currentLessonData.quiz.questions) {
        return;
    }

    const questions = currentLessonData.quiz.questions;
    let score = 0;
    const resultsContainer = document.getElementById('quiz-results');
    const answers = {};

    questions.forEach((q, index) => {
        const selectedOption = document.querySelector(`input[name="question-${index}"]:checked`);
        if (selectedOption) {
            answers[index] = selectedOption.value;
            if (selectedOption.value === q.correctAnswer) {
                score++;
            }
        } else {
            answers[index] = null; 
        }
    });

    resultsContainer.textContent = `Your score: ${score} out of ${questions.length}`;
    resultsContainer.style.display = 'block';
    document.getElementById('complete-button').disabled = false;
    quizActive = true;
    showLessonSection('quiz'); 

    const urlParams = new URLSearchParams(window.location.search);
    const courseName = decodeURIComponent(urlParams.get('course'));

    if (courseName) {
        fetch('/submit-quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                course_name: courseName,
                score: score,
                total_questions: questions.length
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Quiz results submitted successfully:', data.message);
            } else {
                console.error('Error submitting quiz results:', data.error);
            }
        })
        .catch(error => {
            console.error('There was an error submitting the quiz:', error);
        });
    } else {
        console.warn('Course name not available, cannot submit quiz results.');
    }
}

function getLessonData() {
    const urlParams = new URLSearchParams(window.location.search);
    const courseName = urlParams.get('course');
    const moduleName = urlParams.get('module');
    const lessonName = urlParams.get('lesson');

    console.log('Course:', courseName, 'Module:', moduleName, 'Lesson:', lessonName);

    if (!courseName || !moduleName || !lessonName) {
        console.error('Required parameters are missing');
        return;
    }

    const url = `http://127.0.0.1:5000/lesson/${courseName}/${moduleName}/${lessonName}`;
    console.log('Request URL:', url);

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Lesson Data:', data);
            currentLessonData = data;
            document.getElementById('course-title').textContent = data.lesson_title;
            const lessonDescriptionDiv = document.getElementById('lesson-description');
            if (lessonDescriptionDiv) {
                lessonDescriptionDiv.textContent = data.lesson_description;
            }
            const instructorParagraph = document.getElementById('instructor');
            if (instructorParagraph) {
                instructorParagraph.textContent = `Instructor: ${data.instructor}`;
            }

            const contentContainer = document.getElementById('lesson-content');
            if (contentContainer) {
                contentContainer.innerHTML = '';
                if (data.lesson_content && Array.isArray(data.lesson_content)) {
                    data.lesson_content.forEach(step => {
                        const stepDiv = document.createElement('div');
                        stepDiv.classList.add('lesson-step');

                        const title = document.createElement('h4');
                        title.textContent = `Step ${step.step}: ${step.title}`;
                        stepDiv.appendChild(title);

                        const text = document.createElement('p');
                        text.textContent = step.text;
                        stepDiv.appendChild(text);

                        if (step.image) {
                            const img = document.createElement('img');
                            img.src = `${step.image}`;
                            img.alt = step.title;
                            img.style.maxWidth = '100%';
                            img.style.marginTop = '10px';
                            stepDiv.appendChild(img);
                        }

                        contentContainer.appendChild(stepDiv);
                    });
                } else {
                    contentContainer.innerHTML = '<p>No lesson content available.</p>';
                }
            }

            const videoSection = document.getElementById('video-section');
            const videoListContainer = document.getElementById('video-list');

            if (videoSection && videoListContainer) {
                if (data.videos && Array.isArray(data.videos) && data.videos.length > 0) {
                    videoSection.style.display = 'block';
                    videoListContainer.innerHTML = ''; 
                    let currentVideoIndex = 0;
                    let videoElement = null;
                    let nextButton = null;

                    function loadVideo(index) {
                        if (index < data.videos.length) {
                            if (videoElement) {
                                videoElement.pause();
                                videoElement.removeAttribute('src');
                                videoElement.load();
                            }
                            videoElement = document.createElement('video');
                            videoElement.controls = true;
                            videoElement.src = data.videos[index];

                            const listItem = document.createElement('li');
                            listItem.appendChild(videoElement);

                            if (data.videos.length > 1) {
                                if (!nextButton) {
                                    nextButton = document.createElement('button');
                                    nextButton.textContent = 'Next Video';
                                    nextButton.classList.add('next-button');
                                    nextButton.style.display = 'none'; 

                                    nextButton.addEventListener('click', function() {
                                        currentVideoIndex++;
                                        loadVideo(currentVideoIndex);
                                        nextButton.style.display = 'none'; 
                                    });
                                    listItem.appendChild(nextButton);
                                } else {
                                    nextButton.style.display = 'none';
                                }
                            }

                            videoListContainer.innerHTML = '';
                            videoListContainer.appendChild(listItem);

                            videoElement.addEventListener('ended', function() {
                                if (currentVideoIndex < data.videos.length - 1) {
                                    if (nextButton) {
                                        nextButton.style.display = 'inline-block';
                                    }
                                } else {
                                    alert("You have completed all videos for this lesson!");
                                }
                            });
                        } else {
                            alert("No more videos in this lesson.");
                        }
                    }

                    loadVideo(currentVideoIndex); 
                } else {
                    videoSection.style.display = 'none';
                }
            }

            const quizNavButton = document.getElementById('quiz-nav-button');
            const quizQuestionsContainer = document.getElementById('quiz-questions');
            const submitQuizButton = document.getElementById('submit-quiz-button');

            if (data.quiz && data.quiz.questions && data.quiz.questions.length > 0) {
                quizNavButton.style.display = 'inline-block';
                quizQuestionsContainer.innerHTML = '';
                data.quiz.questions.forEach((q, index) => {
                    const questionDiv = document.createElement('div');
                    questionDiv.classList.add('quiz-question');
                    questionDiv.innerHTML = `<p><strong>${index + 1}. ${q.question}</strong></p>`;
                    const optionsDiv = document.createElement('div');
                    optionsDiv.classList.add('quiz-options');
                    q.options.forEach(option => {
                        const radioInput = document.createElement('input');
                        radioInput.type = 'radio';
                        radioInput.name = `question-${index}`;
                        radioInput.value = option;
                        const label = document.createElement('label');
                        label.textContent = option;
                        optionsDiv.appendChild(radioInput);
                        optionsDiv.appendChild(label);
                        optionsDiv.appendChild(document.createElement('br'));
                    });
                    questionDiv.appendChild(optionsDiv);
                    quizQuestionsContainer.appendChild(questionDiv);
                });
                submitQuizButton.onclick = checkQuiz;
                document.getElementById('complete-button').disabled = true;
                quizActive = false;
                showLessonSection('quiz'); 
            } else {
                quizNavButton.style.display = 'none';
                document.getElementById('complete-button').disabled = false;
                quizActive = true;
                showLessonSection('content'); 
            }
        })
        .catch(error => {
            console.error('Error fetching lesson data:', error);
            const contentContainer = document.getElementById('lesson-content');
            if (contentContainer) {
                contentContainer.innerHTML = `<p class="error-message">Failed to load lesson content: ${error.message}</p>`;
            }
            const videoSection = document.getElementById('video-section');
            if (videoSection) {
                videoSection.style.display = 'none';
            }
        });
}

function getCourseData() {
    const urlParams = new URLSearchParams(window.location.search);
    const courseName = urlParams.get('course');

    if (!courseName) {
        console.error('Course name is missing');
        return;
    }

    const url = `http://127.0.0.1:5000/course/${courseName}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Course Data:', data);
            const courseTitleElement = document.getElementById('course-title');
            if (courseTitleElement) {
                courseTitleElement.textContent = data.name;
            }
            const instructorParagraph = document.getElementById('instructor');
            if (instructorParagraph) {
                instructorParagraph.textContent = `Instructor: ${data.teacher ? data.teacher.name : 'N/A'}`;
            }
            const lessonDescriptionDiv = document.getElementById('lesson-description');
            if (lessonDescriptionDiv && data.description) {
                lessonDescriptionDiv.textContent = data.description;
            }

            const modulesContainer = document.getElementById('course-modules');
            if (modulesContainer) {
                modulesContainer.innerHTML = ''; 
                if (data.modules && Array.isArray(data.modules)) {
                    data.modules.forEach(module => {
                        const moduleItem = document.createElement('li');
                        moduleItem.textContent = module.title; 
                        modulesContainer.appendChild(moduleItem);
                    });
                } else {
                    const noModulesMessage = document.createElement('p');
                    noModulesMessage.textContent = 'No modules available for this course.';
                    modulesContainer.appendChild(noModulesMessage);
                }
            }
        })
        .catch(error => {
            console.error('Error fetching course data:', error);
        });
}