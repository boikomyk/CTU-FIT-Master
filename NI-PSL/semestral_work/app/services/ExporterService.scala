package services

import models.data.Note
import play.api.mvc.Result
import play.api.mvc.Results.Ok
import play.api.http.HeaderNames.CONTENT_DISPOSITION
import utils.CsvUtils

import java.time.format.DateTimeFormatter

class ExporterService {
  def exportNoteToCSV(note: Note, filename: String): Result = {
    Ok(
      CsvUtils.makeCsv(List(mapNotePropertiesToCSVFields(note)))
    ).withHeaders(CONTENT_DISPOSITION -> ("attachment; filename=\"" + filename + "\".csv")).as("text/csv")
  }

  def exportNotesToCSV(notes: List[Note], filename: String): Result = {
    Ok(
      CsvUtils.makeCsv(notes.map(note => mapNotePropertiesToCSVFields(note)))
    ).withHeaders(CONTENT_DISPOSITION -> ("attachment; filename=\"" + filename + "\".csv")).as("text/csv")
  }

  private def mapNotePropertiesToCSVFields(note: Note): Map[String, String] = {
    Map(
      "ID" -> note.id.get.toString,
      "Title" -> note.title,
      "Content" -> note.content,
      "Tags" -> note.tags,
      "Created When" -> note.created_when.format(DateTimeFormatter.ofPattern("Y-MM-dd H:m:ss")),
      "Updated When" -> note.updated_when.format(DateTimeFormatter.ofPattern("Y-MM-dd H:m:ss"))
    )
  }
}
