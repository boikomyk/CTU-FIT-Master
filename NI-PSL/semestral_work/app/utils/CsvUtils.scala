package utils

import com.github.tototoshi.csv.CSVWriter

object CsvUtils {
  def makeCsv(rows: List[Map[String, String]]): String = {
    if (rows.isEmpty) {
      throw new Exception("Now rows serialize...")
    } else {
      val headers = rows.flatMap(_.map(_._1)).distinct
      val writer = new java.io.StringWriter()
      val csvWriter = CSVWriter.open(writer)
      csvWriter.writeRow(headers)
      csvWriter.writeAll(rows.map { row => headers.map(header => row.get(header).getOrElse("")).map(csvCellFormat) })
      csvWriter.close()
      writer.toString
    }
  }

  private def csvCellFormat(value: String): String = if (value != null) { value.replace("\r", "\\r").replace("\n", "\\n") } else { "" }
}
