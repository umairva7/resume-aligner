from app.repositories.resume_repository import ResumeRepository

def test_create_and_retrieve_resume(db_session):
    repo = ResumeRepository(db_session)
    resume = repo.create(
        filename="test_resume.pdf",
        file_path="/path/to/test_resume.pdf",
        extracted_text="Experienced Software Engineer"
    )

    assert resume.id is not None
    assert resume.filename == "test_resume.pdf"
    assert resume.is_active is True

    active = repo.get_active_resume()
    assert active is not None
    assert active.id == resume.id
