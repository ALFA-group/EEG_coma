function [paramsOut] = reportGUI(hObject, callbackdata, inputData) %#ok<INUSL>
title = 'Report parameters';
reportModeMenu = {'normal', 'skipReport', 'reportOnly'};
defaultStruct = inputData.userData.report;
reportCallback   = ['defaultFile = get(findobj(''parent'', gcbf, ''tag'', ''sessionFilePath''), ''String'');' ...
    ' [tmpfile tmppath] = uiputfile(''.pdf'', ''Enter filename'', defaultFile); drawnow;' ...
    'if tmpfile ~= 0,' ...
    '    set(findobj(''parent'', gcbf, ''tag'', ''reportName''), ''string'', fullfile(tmppath, tmpfile));' ...
    'end;' ...
    'clear tmpuserdat tmpfile tmppath;'];
summaryCallback   = [' defaultFile = get(findobj(''parent'', gcbf, ''tag'', ''summaryFilePath''), ''String'');' ...
    ' [tmpfile tmppath] = uiputfile(''.html'', ''Enter filename'', defaultFile); drawnow;' ...
    'if tmpfile ~= 0,' ...
    '    set(findobj(''parent'', gcbf, ''tag'', ''summaryName''), ''string'', fullfile(tmppath, tmpfile));' ...
    'end;' ...
    'clear tmpuserdat tmpfile tmppath;'];
while(true)
    mainFigure = findobj('Type', 'Figure', '-and', 'Name', inputData.name);
    userdata = get(mainFigure, 'UserData');
    if isempty(userdata) || ~isfield(userdata, 'report')
        paramsOut = struct();
    else
        paramsOut = userdata.report;
    end
    [defaultStruct, errors] = checkStructureDefaults(paramsOut, defaultStruct);
    
    if ~isempty(errors)
        warning('reportGUI:bad parameters', getMessageString(errors)); %#ok<CTPCT>
    end
    if defaultStruct.publishOn.value
        publishCheckValue = 1;
    else
        publishCheckValue = 0;
    end
    %creates a structure for the text color of each parameter and sets them
    %all to black
    fNamesDefault = fieldnames(defaultStruct);
    for k = 1:length(fNamesDefault)
        textColorStruct.(fNamesDefault{k}) = 'k';
    end
    reportModeValue = typeMenuPosition(...
        defaultStruct.reportMode.value, reportModeMenu);
    report = defaultStruct.sessionFilePath.value;
    summary = defaultStruct.summaryFilePath.value;
    geometry = {[1,1,2], [1, 3],  [1,2,1], [1,2,1]};
    geomvert = [];
    closeOpenWindows(title);
    uilist = {{'style', 'text', 'string', 'Report mode', ...
        'TooltipString', defaultStruct.reportMode.description}...
        {'style', 'popupmenu', 'string', 'Normal|Skip|Report only', ...
        'value', reportModeValue, 'tag', 'reportMode', ...
        'ForegroundColor', textColorStruct.reportMode}...
        {'style', 'text', 'string', ''}...
        {'style', 'text', 'string', 'Publish on', ...
        'TooltipString', defaultStruct.publishOn.description}...
        {'style', 'checkbox', 'Value', publishCheckValue, ...
        'tag', 'publishOn', 'ForegroundColor', textColorStruct.publishOn}...
        {'style', 'text', 'string', 'Report file name'}...
        {'style', 'edit', 'string', report, 'tag', 'sessionFilePath', 'userdata', 'sessionFilePath'}...
        {'style', 'pushbutton', 'string', 'Browse', 'callback', reportCallback, 'userdata', 'reportName'}...
        {'style', 'text', 'string', 'Summary file name'}...
        {'style', 'edit', 'string', summary, 'tag', 'summaryFilePath'}...
        {'style', 'pushbutton', 'string', 'Browse', 'callback', summaryCallback, 'userdata', 'summaryFilePath'}};
    [~, ~, ~, paramsOut] = inputgui('geometry', geometry, ...
        'geomvert', geomvert, 'uilist', uilist, 'title', title, ...
        'helpcom', 'pophelp(''pop_prepPipeline'')');
    if isempty(paramsOut)
        break;
    end
    paramsOut.consoleFID = num2str(defaultStruct.consoleFID.value);
    paramsOut.reportMode = ...
        typeMenuString(paramsOut.reportMode, reportModeMenu);
    [paramsOut, typeErrors, fNamesErrors] = ...
        changeType(paramsOut, defaultStruct);
    mainFigure = findobj('Type', 'Figure', '-and', 'Name', inputData.name);
    userdata = get(mainFigure, 'UserData');
    userdata.report = paramsOut;
    set(mainFigure, 'UserData', userdata);
    if isempty(typeErrors)
        break;
    end
    textColorStruct = highlightErrors(fNamesErrors, ...
        fNamesDefault, textColorStruct);
    displayErrors(typeErrors); % Displays the errors and restarts GUI
end

    function position = typeMenuPosition(theString, menuString)
        menuIndex = 1:length(menuString);
        position = strcmpi(theString, menuString);
        position = menuIndex(position);
    end

    function theString = typeMenuString(position, menuString)
        theString = menuString{position};
    end

end