from manim import *

class BaseStableParition(MovingCameraScene):
	ARRAY_SIZE = 10
	FIRST_ELEMENT_OFFSET = ARRAY_SIZE/2.0

	def createArray(self, up):
		squares=[Square().set_stroke(color=GRAY) for i in range(self.ARRAY_SIZE)]

		squares[0].move_to(self.FIRST_ELEMENT_OFFSET * LEFT + up * UP)

		for i in range(1, self.ARRAY_SIZE):
			squares[i].next_to(squares[i-1], RIGHT)

		self.bring_to_back(*squares)

		return squares
	
	def createElements(self):
		squares=[Square() for _ in range(self.ARRAY_SIZE)]
		texts=[Text(str(i)).scale(2) for i in range(self.ARRAY_SIZE)]

		for i, (square, text) in enumerate(zip(squares, texts)):
			colour = RED if i % 2 == 0 else BLUE
			square.set_stroke(color=colour)
			text.set_color(colour)

		elements = [VGroup(square, text) for square, text in zip(squares, texts)]

		return elements

	def setupArray(self, elements, mainArray, shift = None):
		mainArrayVGroup = VGroup(*mainArray)
		elementsVGroup = VGroup(*elements)
		
		self.add(mainArrayVGroup)

		for element, array in zip(elements, mainArray):
			element.move_to(array)
		self.play(Create(elementsVGroup), run_time=3)

		if shift is not None:
			self.play(mainArrayVGroup.animate.shift(shift), elementsVGroup.animate.shift(shift))

class AdditionalMemory(BaseStableParition):
	START_SHIFT = 1.5 * UP

	def setupTempArray(self, tempArray):
		self.play(*[Create(e) for e in tempArray])
		self.bring_to_back(*tempArray)

	def moveToTemp(self, elements, mainArray, tempArray):

		pointerOrigin = Dot(point=ORIGIN, color=GREEN).next_to(mainArray[0], UP)
		pointerTargetFirst = Dot(point=ORIGIN, color=RED).next_to(tempArray[0], DOWN)
		pointerTargetLast = Dot(point=ORIGIN, color=BLUE).next_to(tempArray[-1], DOWN)

		self.play(Create(pointerOrigin))
		self.play(Create(pointerTargetFirst), Create(pointerTargetLast))


		for i in range(self.ARRAY_SIZE):
			moveTo = i/2 if i % 2 == 0 else self.ARRAY_SIZE - (i+1)/2
			pointerMove = pointerTargetFirst if i % 2 == 0 else pointerTargetLast

			if i != 0:
				self.play(pointerOrigin.animate.next_to(mainArray[i], UP))

			self.play(elements[i].animate.move_to(tempArray[int(moveTo)]))

			addSub = 1 if i % 2 == 0 else -1 
			pointerMove.next_to(tempArray[int(moveTo) + addSub], DOWN)


		self.play(FadeOut(pointerOrigin), FadeOut(pointerTargetLast))

		return pointerTargetFirst

	def moveToMain(self, elements, mainArray, tempArray):
		pointerOrigin = Dot(point=ORIGIN, color=GREEN).next_to(mainArray[0], UP)
		self.add(pointerOrigin)
		pointerTargetFirst = Dot(point=ORIGIN, color=RED).next_to(tempArray[0], DOWN)
		self.add(pointerTargetFirst)
		pointerTargetLast = Dot(point=ORIGIN, color=BLUE).next_to(tempArray[-1], DOWN)

		for i in range(0, self.ARRAY_SIZE, 2):
			target = int(i/2)
			if i != 0:
				self.play(pointerTargetFirst.animate.next_to(tempArray[target], DOWN))
			self.play(elements[i].animate.move_to(mainArray[target]))
			pointerOrigin.next_to(mainArray[target+1], UP)
			
		pointerPartition = Dot(point=ORIGIN, color=GOLD).next_to(mainArray[5], UP)
		self.remove(pointerTargetFirst)
		self.add(pointerPartition, pointerTargetLast)

		for i in range(1, self.ARRAY_SIZE, 2):
			iHalf = int(i/2)
			target = int((self.ARRAY_SIZE+i)/2)
			if i != 1:
				self.play(pointerTargetLast.animate.next_to(tempArray[self.ARRAY_SIZE - iHalf - 1], DOWN))
			self.play(elements[i].animate.move_to(mainArray[target]))
			if target+1 != self.ARRAY_SIZE:
				pointerOrigin.next_to(mainArray[target+1], UP)
		
		self.remove(pointerOrigin, pointerTargetLast)

		return pointerPartition

	def cleanupArray(self, elements, mainArray, tempArray, paritionPoint):
		mainArrayVGroup = VGroup(*mainArray)
		elementsVGroup = VGroup(*elements)

		self.play(*[FadeOut(e) for e in tempArray])

		shiftGroup = VGroup(mainArrayVGroup, elementsVGroup, paritionPoint)
		self.play(shiftGroup.animate.shift(-self.START_SHIFT))

		#self.play(*[FadeOut(e) for e in mainArray], *[FadeOut(e) for e in elements], FadeOut(paritionPoint));

	def construct(self):

		self.camera.frame.set(width=(self.ARRAY_SIZE+2)*2).move_to(self.ARRAY_SIZE/2.0 * RIGHT)

		elements = self.createElements()
		mainArray = self.createArray(0)
		tempArray = self.createArray(-1.5)
		
		self.setupArray(elements, mainArray, self.START_SHIFT)
		self.setupTempArray(tempArray)
		self.wait(2)

		paritionPointTemp = self.moveToTemp(elements, mainArray, tempArray)
		paritionPointTemp.set_color(GOLD)
		self.wait(2)

		paritionPointMain = self.moveToMain(elements, mainArray, tempArray)
		self.remove(paritionPointTemp)
		self.wait(2)

		self.cleanupArray(elements, mainArray, tempArray, paritionPointMain)

		self.wait()

class InPlace(BaseStableParition):
	def mark(self, dots, start, end):
		if end - start == 1:
			self.play(Create(dots[start]))
			self.remove(dots[start])
			return

		connection = Line(dots[start], dots[end-1])
		self.play(Create(connection))
		return connection

	def findPivot(self, elements, start, stop):
		for i in range(start, stop):
			if elements[i] % 2 == 1:
				return i
		return stop

	def rotate(self, values, start, middle, stop):
		temp = []
		for i in range(start, middle):
			temp.append(values[i])
		
		firstSize = middle - start
		secondSize = stop - middle

		for i in range(secondSize):
			values[start + i] = values[middle+i]
		
		for i in range(firstSize):
			values[start + secondSize + i] = temp[i]

	def devide(self, elements, values, mainArray, dots, start, stop):
		if start == stop:
			return
		
		diff = stop - start

		if diff == 1:
			self.mark(dots, start, stop)
			return 

		offset = start + int(diff / 2)

		self.devide(elements, values, mainArray, dots, start, offset)
		self.devide(elements, values, mainArray, dots, offset, stop)

		markLine = self.mark(dots, start, stop)

		pivot1 = self.findPivot(values, start, offset)
		pivot2 = self.findPivot(values, offset, stop)

		if pivot1 != offset and pivot2 != offset:
			first = VGroup(*[elements[i] for i in range(pivot1, offset)])
			second = VGroup(*[elements[i] for i in range(offset, pivot2)])

			self.play(first.animate.shift(-2.25*UP))
			shiftSecond = offset - pivot1
			self.play(second.animate.shift(2.25*shiftSecond*LEFT))
			shiftFirst = pivot2 - offset
			self.play(first.animate.shift(2.25*UP + 2.25*shiftFirst*RIGHT))

			self.rotate(values, pivot1, offset, pivot2)
			self.rotate(elements, pivot1, offset, pivot2)

		self.remove(markLine)


	def construct(self):

		self.camera.frame.set(width=(self.ARRAY_SIZE+2)*2).move_to(self.ARRAY_SIZE/2.0 * RIGHT)

		elements = self.createElements()
		values = [i for i in range(self.ARRAY_SIZE)]
		mainArray = self.createArray(0)
		dots = [Dot() for _ in range(self.ARRAY_SIZE)]
		
		self.setupArray(elements, mainArray)
		for dot, array in zip(dots, mainArray):
			dot.next_to(array, UP)
		
		self.devide(elements, values, mainArray, dots, 0, self.ARRAY_SIZE)

		self.wait()

class InPlace2(BaseStableParition):
	
	INITIAL_UP = 5

	def arrayShift(self, elements, mainArray, direction):
		group = VGroup(*elements, *mainArray)
		self.play(group.animate.shift(self.INITIAL_UP * direction))
		self.bring_to_front(*elements)

	def mark(self, dots, start, end):
		if end - start == 1:
			self.add(dots[start])
			return dots[start]

		connection = Line(dots[start], dots[end-1])
		self.add(connection)
		return connection

	def findPivot(self, elements, start, stop):
		for i in range(start, stop):
			if elements[i] % 2 == 1:
				return i
		return stop

	def rotate(self, values, start, middle, stop):
		temp = []
		for i in range(start, middle):
			temp.append(values[i])
		
		firstSize = middle - start
		secondSize = stop - middle

		for i in range(secondSize):
			values[start + i] = values[middle+i]
		
		for i in range(firstSize):
			values[start + secondSize + i] = temp[i]

	def devide(self, elements, values, mainArray, dots, level, start, stop):
		if start == stop:
			return
		
		diff = stop - start
		shiftHeight = 2.2

		markLine = self.mark(dots, start, stop)

		groupAll = VGroup(*[elements[i] for i in range(start, stop)])
		if level != 0:
			self.play(groupAll.animate.shift(shiftHeight*DOWN))

		self.remove(markLine)

		if diff == 1:
			return 

		offset = start + int(diff / 2)

		self.devide(elements, values, mainArray, dots, level+1, start, offset)
		self.devide(elements, values, mainArray, dots, level+1, offset, stop)

		self.add(markLine)

		pivot1 = self.findPivot(values, start, offset)
		pivot2 = self.findPivot(values, offset, stop)

		if pivot1 != offset and pivot2 != offset:
			first = VGroup(*[elements[i] for i in range(pivot1, offset)])
			second = VGroup(*[elements[i] for i in range(offset, pivot2)])

			shiftSecond = offset - pivot1
			shiftFirst = pivot2 - offset
			if level < 3:
				self.play(first.animate.shift(-2.25*UP))
				self.play(second.animate.shift(2.25*shiftSecond*LEFT))
				self.play(first.animate.shift(2.25*UP + 2.25*shiftFirst*RIGHT))
			else:
				self.play(second.animate.shift(2.25*shiftSecond*LEFT), first.animate.shift(2.25*shiftFirst*RIGHT))

			self.rotate(values, pivot1, offset, pivot2)
			self.rotate(elements, pivot1, offset, pivot2)
		
		self.play(groupAll.animate.shift(shiftHeight*UP))
		self.remove(markLine)

	def construct(self):

		self.camera.frame.set(width=(self.ARRAY_SIZE+2)*2).move_to(self.ARRAY_SIZE/2.0 * RIGHT)

		elements = self.createElements()
		values = [i for i in range(self.ARRAY_SIZE)]
		mainArray = self.createArray(0)
		dots = [Dot() for _ in range(self.ARRAY_SIZE)]
		
		self.setupArray(elements, mainArray)

		self.arrayShift(elements, mainArray, UP)
		for dot, array in zip(dots, mainArray):
			dot.next_to(array, UP)
		
		self.devide(elements, values, mainArray, dots, 0, 0, self.ARRAY_SIZE)
		
		self.arrayShift(elements, mainArray, DOWN)
		self.wait()
