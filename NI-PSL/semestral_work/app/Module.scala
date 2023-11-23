import com.google.inject.{AbstractModule, Provides}
//import com.hhandoko.play.pdf.PdfGenerator
import dependency_injection.DatabaseEngine
import _root_.play.api.Environment


class Module extends AbstractModule {
  override def configure(): Unit = {
    bind(classOf[DatabaseEngine]).asEagerSingleton()
  }
//
//  /**
//   * Provides PDF generator implementation.
//   *
//   * @param env The current Play app Environment context.
//   * @return PDF generator implementation.
//   */
//  @Provides
//  def providePdfGenerator(env: Environment): PdfGenerator = {
//    val pdfGen = new PdfGenerator(env)
//    pdfGen.loadLocalFonts(Seq("fonts/opensans-regular.ttf"))
//    pdfGen
//  }
}
