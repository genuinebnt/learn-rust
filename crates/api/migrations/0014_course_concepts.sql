-- Which of a course's concept articles the owner has marked as read. A row means read; unmarking deletes it.
CREATE TABLE course_concept_state (
    course  text        NOT NULL,
    concept text        NOT NULL,
    read_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (course, concept)
);
