USE [nip]
GO
/****** Object:  UserDefinedFunction [dbo].[com_udfGetZeroPad]    Script Date: 9/7/2020 12:52:31 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

create FUNCTION [dbo].[com_udfGetZeroPad]
(
	@InputString varchar(32), 
	@Lenght tinyint
) 
RETURNS varchar(32)
 AS
BEGIN
	DECLARE @ZeroString varchar(32)
	SET @ZeroString = '00000000000000000000000000000000'
	RETURN RIGHT(@ZeroString + @InputString, @Lenght)
END
GO
/****** Object:  View [dbo].[ShiftAssignmentPivoted]    Script Date: 9/7/2020 12:52:31 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


CREATE view [dbo].[ShiftAssignmentPivoted]
AS
SELECT ROW_NUMBER() over(order by YearWorkingPeriod, PersonnelBaseId, [Rank])  as id,
	* 
FROM   
(
    SELECT 
	  ps.WorkSection_Id WorkSection
	  ,ps.YearWorkingPeriod
	  ,ps.Cost
	  ,ps.[Rank]
	  ,ps.PersonnelBaseId
	  ,P.FullName
	  ,P.PersonnelTypes_id  
      ,'D'+dbo.com_udfGetZeroPad([Day],2) [Day]
      ,ps.Shift	  
	FROM 
		[nip_personnelshiftdateassignments] PS	
		JOIN nip_personnel P ON P.PersonnelBaseId = PS.PersonnelBaseId			
) t 
PIVOT(
    sum(Shift) 
    FOR [Day] IN ([D01],[D02],[D03],[D04],[D05],[D06],[D07],[D08],[D09],[D10],
				  [D11],[D12],[D13],[D14],[D15],[D16],[D17],[D18],[D19],[D20],
				  [D21],[D22],[D23],[D24],[D25],[D26],[D27],[D28],[D29],[D30],
				  [D31]
        )
) AS pivot_table;
GO
/****** Object:  View [dbo].[ShiftAssignmentPivoted_by_id]    Script Date: 9/7/2020 12:52:31 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO








CREATE view [dbo].[ShiftAssignmentPivoted_by_id]
AS
SELECT * FROM   
(
    SELECT 
	   ps.WorkSection_id WorkSection
	  ,ps.YearWorkingPeriod
	  ,ps.Cost
	  ,ps.[Rank]
	  ,ps.PersonnelBaseId
	  ,P.FullName
	  ,P.PersonnelTypes_id	  
      ,'D'+dbo.com_udfGetZeroPad([Day],2) [Day]
      ,ps.Shift	  
	FROM 
		[dbo].[nip_personnelshiftdateassignments] PS	
		JOIN nip_personnel P ON P.PersonnelBaseId = PS.PersonnelBaseId			
) t 
PIVOT(
    sum(Shift) 
    FOR [Day] IN ([D01],[D02],[D03],[D04],[D05],[D06],[D07],[D08],[D09],[D10],
				  [D11],[D12],[D13],[D14],[D15],[D16],[D17],[D18],[D19],[D20],
				  [D21],[D22],[D23],[D24],[D25],[D26],[D27],[D28],[D29],[D30],
				  [D31]
        )
) AS pivot_table;
GO
/****** Object:  StoredProcedure [dbo].[com_SetDimDate]    Script Date: 9/7/2020 12:52:31 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE proc [dbo].[com_SetDimDate]
AS
DECLARE @D0 SMALLDATETIME = '2005-01-01'
DECLARE @DateKey VARCHAR(20)
      ,@Date SMALLDATETIME
      ,@Per_Date VARCHAR(20)
      ,@Per_Year INT
      ,@Per_Season INT
      ,@Per_Month INT
	  ,@Per_FirstOfYearDate varchar(20)
	  ,@Per_DayInYear INT
	  ,@Per_DayInMonth INT
      ,@Per_WeekNoInMonth INT
      ,@Per_WeekNoInYear INT
      ,@Per_WeekDay INT
	  ,@PersianSemester INT
	  ,@PersianSemesterTitle nvarchar(100)
	  ,@FiscalYear int	  
      ,@Per_YearTitle NVARCHAR(20)
      ,@Per_SeasonTitle NVARCHAR(20)
      ,@Per_MonthTitle NVARCHAR(20)
      ,@Per_weekDayTitle NVARCHAR(20)
      ,@WeekDay INT
      ,@WeekDayTitle VARCHAR(20)
	  ,@WorkingPriodIndex INT
	  ,@WorkingPriodTitle VARCHAR(50)
WHILE (@D0 < = '2050-01-30')
BEGIN
	SELECT @Date = @D0
	SELECT @Per_Date = [DBO].com_udfGetSolarDate(@Date)
	SELECT @Per_Year = SUBSTRING(@Per_Date,1,4)
	SELECT @Per_YearTitle = SUBSTRING(@Per_Date,1,4)
	SELECT @Per_Month = SUBSTRING(@Per_Date,6,2)
	
	SELECT @Per_Season = CASE 
							WHEN @Per_Month <= 3 THEN 1
							WHEN @Per_Month >= 4 AND @Per_Month <= 6 THEN 2
							WHEN @Per_Month >= 7 AND @Per_Month <= 9 THEN 3
							WHEN @Per_Month >= 10 AND @Per_Month <= 12 THEN 4
							ELSE 0 END
	SELECT @Per_YearTitle = [dbo].com_GetPersianDateVarchar(@Per_Year)
	SELECT @Per_SeasonTitle = CASE 
								WHEN @Per_Season = 1 THEN 'بهار'
								WHEN @Per_Season = 2 THEN 'تابستان'
								WHEN @Per_Season = 3 THEN 'پاییز'
								WHEN @Per_Season = 4 THEN  'زمستان'
								ELSE '' END
	SELECT @Per_MonthTitle = CASE 
								WHEN @Per_Month = 1 THEN 'فروردین'
								WHEN @Per_Month = 2 THEN 'اردیبهشت'
								WHEN @Per_Month = 3 THEN 'خرداد'
								WHEN @Per_Month = 4 THEN 'تیر'
								WHEN @Per_Month = 5 THEN 'مرداد'
								WHEN @Per_Month = 6 THEN 'شهریور'
								WHEN @Per_Month = 7 THEN 'مهر'
								WHEN @Per_Month = 8 THEN 'آبان'
								WHEN @Per_Month = 9 THEN 'آذر'
								WHEN @Per_Month = 10 THEN 'دی'
								WHEN @Per_Month = 11 THEN 'بهمن'
								WHEN @Per_Month = 12 THEN 'اسفند'
								ELSE '' END
	SELECT @Per_WeekDay =	CASE 
								WHEN DATEPART(WEEKDAY,@Date) = 1 THEN 2
								WHEN DATEPART(WEEKDAY,@Date) = 2 THEN 3
								WHEN DATEPART(WEEKDAY,@Date) = 3 THEN 4 
								WHEN DATEPART(WEEKDAY,@Date) = 4 THEN 5
								WHEN DATEPART(WEEKDAY,@Date) = 5 THEN 6 
								WHEN DATEPART(WEEKDAY,@Date) = 6 THEN 7 
								WHEN DATEPART(WEEKDAY,@Date) = 7 THEN 1
								ELSE 0 END
	SELECT @Per_weekDayTitle =CASE 
								WHEN DATEPART(WEEKDAY,@Date) = 1 THEN 'یکشنبه'
								WHEN DATEPART(WEEKDAY,@Date) = 2 THEN 'دوشنبه'
								WHEN DATEPART(WEEKDAY,@Date) = 3 THEN 'سه شنبه'
								WHEN DATEPART(WEEKDAY,@Date) = 4 THEN 'چهارشنبه'
								WHEN DATEPART(WEEKDAY,@Date) = 5 THEN 'پنجشنبه'
								WHEN DATEPART(WEEKDAY,@Date) = 6 THEN 'جمعه'
								WHEN DATEPART(WEEKDAY,@Date) = 7 THEN 'شنبه'
								ELSE '' END
	SELECT @Per_FirstOfYearDate = CAST(@Per_Year AS VARCHAR(4)) + '/01/01' 
	
	SELECT @Per_DayInYear = DATEDIFF(DAY,DBO.com_udfGetChristianDate(@Per_FirstOfYearDate),@Date)	 
	SELECT @Per_WeekNoInYear = @Per_DayInYear / 7
	SELECT @Per_DayInMonth = CASE 
								WHEN @Per_Month<10 THEN DATEDIFF(DAY,DBO.com_udfGetChristianDate(CAST(@Per_Year AS VARCHAR(4)) +'/0' + CAST(@Per_Month AS VARCHAR(2)) +'/01' ),@Date)
								ELSE DATEDIFF(DAY,DBO.com_udfGetChristianDate(CAST(@Per_Year AS VARCHAR(4)) +'/' + CAST(@Per_Month AS VARCHAR(2)) +'/01' ),@Date) END + 1
	SELECT @Per_WeekNoInMonth = @Per_DayInMonth / 7
	SELECT @PersianSemester = CASE WHEN @Per_Month <= 6 THEN 1 ELSE 2 END
	SELECT @PersianSemesterTitle = CASE WHEN @PersianSemester = 1 THEN 'نیمسال اول' ELSE 'نیمسال دوم' END
	SELECT @FiscalYear = @Per_Year

	SELECT @WeekDay = DATEPART(WEEKDAY,@Date)
	SELECT @WeekDayTitle =	CASE 
								WHEN DATEPART(WEEKDAY,@Date) = 1 THEN 'SUN'
								WHEN DATEPART(WEEKDAY,@Date) = 2 THEN 'MON'
								WHEN DATEPART(WEEKDAY,@Date) = 3 THEN 'TUE'
								WHEN DATEPART(WEEKDAY,@Date) = 4 THEN 'THR'
								WHEN DATEPART(WEEKDAY,@Date) = 5 THEN 'WEN'
								WHEN DATEPART(WEEKDAY,@Date) = 6 THEN 'FRI'
								WHEN DATEPART(WEEKDAY,@Date) = 7 THEN 'SAT'
								ELSE '' END	
	INSERT INTO nip_dim_date
		SELECT @Date [Date]
			  ,@Per_Date [PersianDate]
			  ,CASE WHEN @Per_WeekDay =7 THEN 1 ELSE 0 END [SpecialDay]
			  ,@Per_Year [PersianYear]			  
			  ,@Per_YearTitle [PersianYearTitle]
			  ,@FiscalYear [FiscalYear]
			  ,null [WorkingPriodYear]
			  ,null [WorkingPeriod]
			  ,null [WorkingPeriodTitle]
			  ,@PersianSemester [PersianSemester]
 			  ,@PersianSemesterTitle [PersianSemesterTitle]
			  ,@Per_Season [PersianQuarter]
			  ,@Per_SeasonTitle [PersianQuarterTitle]
			  ,@Per_Month [PersianMonth]
			  ,@Per_MonthTitle [PersianMonthTitle]
			  ,@Per_WeekNoInYear [PersianWeekNumberOfYear]
			  ,@Per_WeekNoInMonth [PersianWeekNumberOfMonth]
			  ,@Per_DayInMonth [PersianDayOfMonth]	
			  ,@Per_DayInYear [PersianDayOfYear]
			  ,@Per_WeekDay [PersianWeekDay]			  			  			  
			  ,@Per_weekDayTitle [PersianWeekDayTitle]			  
			  -------------------------------------			  		  			  			  		  			  			  
			  --,@WeekDay [WeekDay]
			  --,@WeekDayTitle [WeekDayTitle]													
    
     
      
     
			       			  			       
	SET @D0 = DATEADD(DAY,1,@D0)
END
GO
/****** Object:  StoredProcedure [dbo].[UpdateLastRanks]    Script Date: 9/7/2020 12:52:31 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE proc [dbo].[UpdateLastRanks](@WorkSectionId int, @YearWorkingPeriod int)
AS
UPDATE [nip_shiftassignments]
SET [Rank] = T.[Rank]
FROM [nip_shiftassignments] JOIN
	 (SELECT distinct
		   ROW_NUMBER() over(order by [Cost],[EndTime]) [Rank]
		  ,[Cost] 
			,[EndTime]  
		  ,[WorkSection_id]
		  ,[YearWorkingPeriod]
	  FROM [nip_shiftassignments]
	  WHERE WorkSection_id = @WorkSectionId
			  AND YearWorkingPeriod = @YearWorkingPeriod
	  GROUP BY
		   [Cost]      
		  ,[EndTime]
		  ,[WorkSection_id]
		  ,[YearWorkingPeriod]
	) T ON 
	  [nip_shiftassignments].YearWorkingPeriod = 
	  t.YearWorkingPeriod AND
	  [nip_shiftassignments].WorkSection_id = 
	  t.WorkSection_id AND
	  [nip_shiftassignments].Cost = t.Cost AND
	  [nip_shiftassignments].EndTime = t.EndTime 
GO
/****** Object:  StoredProcedure [dbo].[UpdateUsedParentCount]    Script Date: 9/7/2020 12:52:31 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE proc [dbo].[UpdateUsedParentCount](@WorkSectionId int, @YearWorkingPeriod int, @RANK int)
AS
UPDATE [nip_shiftassignments]
SET [UsedParentCount] += 1
FROM [nip_shiftassignments] 
WHERE WorkSection_id = @WorkSectionId 
      AND YearWorkingPeriod = @YearWorkingPeriod
      AND RANK = @RANK
GO
