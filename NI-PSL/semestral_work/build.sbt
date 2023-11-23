name := """semestral_work"""
organization := "fit.cvut"

version := "1.0-SNAPSHOT"

lazy val root = (project in file(".")).enablePlugins(PlayScala)

scalaVersion := "2.13.8"

libraryDependencies += guice
libraryDependencies += "org.scalatestplus.play" %% "scalatestplus-play" % "5.1.0" % Test
libraryDependencies += "org.webjars" % "bootstrap" % "5.1.1"


// Adds additional packages into Twirl
//TwirlKeys.templateImports += "fit.cvut.controllers._"

// Adds additional packages into conf/routes
// play.sbt.routes.RoutesKeys.routesImport += "fit.cvut.binders._"
//libraryDependencies += "com.typesafe.play" %% "play-slick" % "5.0.0"
//libraryDependencies += "com.typesafe.play" %% "play-slick-evolutions" % "5.0.0"
libraryDependencies += "com.typesafe.slick" %% "slick" % "3.3.3"
libraryDependencies += "com.h2database" % "h2" % "2.1.210"
libraryDependencies ++= Seq(
  "com.hhandoko" %% "play28-scala-pdf" % "4.3.0" // Use `play27-scala-pdf` for Play 2.7.x apps, etc.
)
resolvers ++= Seq(
  Resolver.sonatypeRepo("snapshots")
)

libraryDependencies += "com.github.tototoshi" %% "scala-csv" % "1.3.10"